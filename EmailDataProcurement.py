from __future__ import print_function
import sys
import json
import base64
import socket
import os.path
from config import *
from pprint import pprint
from bs4 import BeautifulSoup
from google.api_core import retry
from google.cloud import pubsub_v1
from google.oauth2 import service_account
from googleapiclient.discovery import build
from concurrent.futures import TimeoutError
from DataPreparation import DataPreparation
from google.oauth2.credentials import Credentials
from google.auth import load_credentials_from_file
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


class EmailDataProcurement:
	"""
	This class can be used to establish gmail API read, watch and pub/sub message retrival.
	"""
	def __init__(self):
		# loading credentials
		self.creds = self.load_credentatials(PATH_TO_CRED)

		# connecting to gmail API object
		self.gmail = build('gmail', 'v1', credentials=self.creds)

		# data processing object
		self.data_pro_obj = DataPreparation(creds=self.creds, connect_db=False)

		self.EMAILS_TO_PROCESS_AT_UPDATE = 50

		self.lock = False

	@staticmethod
	def generate_credential_token(path_to_cred=PATH_TO_CRED, path_to_token=PATH_TO_TOKEN):
		"""
		This class method can be used to load/generate access token for gmail & pubsub api.
		Args:
			path_to_cred: path to the desktop credention json file.
			path_to_token: path to the saved token file.
		"""
		# Variable creds will store the user access token.
		# If no valid token found, we will create one.
		creds = None

		# The file token.pickle contains the user access token.
		# Check if it exists
		if os.path.exists(path_to_token):
			# Read the token from the file and store it in the variable creds
			creds = Credentials.from_authorized_user_file(path_to_token, SCOPES)

		# If credentials are not available or are invalid, ask the user to log in.
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(path_to_cred, SCOPES)
				creds = flow.run_local_server(port=0)

			# Save the access token in token.pickle file for the next run
			with open(path_to_token, 'w') as token:
				token.write(creds.to_json())
		print("\nCredentials ready\n")
		return creds

	@staticmethod
	def load_credentatials(path_to_key):
		if os.path.exists(path_to_key):
			credentials = service_account.Credentials.from_service_account_file(path_to_key, scopes=SCOPES)
			delegated_credentials = credentials.with_subject(EMAIL)
			return delegated_credentials
		else:
			print("Service account credentials path incorrect")
			return None

	def stop_the_push_service(self):
		"""
		This method can be used to stio the gmail API watch.
		Returns:
			None
		"""
		self.gmail.users().stop(userId='me').execute()
		print("\nGmail watch stopped..")
		return

	def start_the_push_service(self):
		"""
		This method can used to start the gmail API watch.
		Returns:
			None
		"""
		# stop the earlier watch call
		self.stop_the_push_service()

		request = {
			'labelIds': ['INBOX'],
			'topicName': 'projects/'+PROJECT_ID+'/topics/'+TOPIC_ID,
			'labelFilterAction': 'INCLUDE'
		}
		watch_response = self.gmail.users().watch(userId='me', body=request).execute()
		# Save the access token in token.pickle file for the next run

		with open(PATH_TO_SAVE_WATCH_RESPONSE, 'w') as fp:
			json.dump(watch_response, fp)
		print("\nStarted the watch successfully")
		print("Watch response: {}\n".format(watch_response))
		return

	def get_num_messages_in_subscription(self):

		subscriber = pubsub_v1.SubscriberClient(credentials=self.creds)
		subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

		NUM_MESSAGES = 100

		# Wrap the subscriber in a 'with' block to automatically call close() to
		# close the underlying gRPC channel when done.

		with subscriber:
			# The subscriber pulls a specific number of messages. The actual
			# number of messages pulled may be smaller than max_messages.
			response = subscriber.pull(
				request={"subscription": subscription_path, "max_messages": NUM_MESSAGES},
				retry=retry.Retry(deadline=300),
			)

			# ack_ids = []
			# for received_message in response.received_messages:
			# 	ack_ids.append(received_message.ack_id)
			if len(response.received_messages)>0:
				# # Acknowledges the received messages so they will not be sent again.
				# subscriber.acknowledge(request={"subscription": subscription_path, "ack_ids": ack_ids})
				# print(f"Received and acknowledged {len(response.received_messages)} messages from {subscription_path}.")
				return len(response.received_messages)
			else:
				return self.EMAILS_TO_PROCESS_AT_UPDATE

	def callback(self, message):
		"""
		This method is callback to retrieve the message data.
		Args:
			message: Object of the class Message.

		Returns:
			None
		"""
		email_num = self.EMAILS_TO_PROCESS_AT_UPDATE #self.get_num_messages_in_subscription()
		if not self.lock:
			self.lock = True
			print("\nThere are updates in the inbox..")
			if email_num:
				recent_email_information = self.get_emails(number_of_emails=email_num)
				print(recent_email_information)
				# updated_rows = self.data_pro_obj.update_to_database(email_data=recent_email_information)
				# self.data_pro_obj.update_expense_excel(updated_rows)
				self.EMAILS_TO_PROCESS_AT_UPDATE = EMAILS_TO_PROCESS_AT_UPDATE
				self.lock = False
			print("\nWaiting for updates in inbox..")
		message.ack()

	def start_pubsub_communication(self, timeout=None):
		"""
		This method is used to constantly monitor asynchronous pub/sub pull messages.
		Args:
			timeout{int}: Time(sec) after which the monitor should be stopped.
		Returns:
			None
		"""

		subscriber = pubsub_v1.SubscriberClient(credentials=self.creds)
		# The `subscription_path` method creates a fully qualified identifier
		# in the form `projects/{project_id}/subscriptions/{subscription_id}`
		subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

		streaming_pull_future = subscriber.subscribe(subscription_path, callback=self.callback)
		print(f"Listening for messages on {subscription_path}..\n")

		# Wrap subscriber in a 'with' block to automatically call close() when done.
		with subscriber:
			try:
				# When `timeout` is not set, result() will block indefinitely,
				# unless an exception is encountered first.
				streaming_pull_future.result(timeout=timeout)
			except TimeoutError:
				streaming_pull_future.cancel()
			except socket.timeout:
				streaming_pull_future.cancel()
				print("socket timeout")
				sys.exit()
			except KeyboardInterrupt:
				streaming_pull_future.cancel()
				print("KeyboardInterrupt")
				sys.exit()
		return

	def get_emails(self, number_of_emails=15):
		"""
		This function can be used to read recent emails from the inbox.
		Args:
			number_of_emails{int}: number of emails to be read
		Returns:
			recent_email_data: Returns json contains latest email data.
		"""

		# request a list of all the messages
		# result = self.gmail.users().messages().list(userId='me').execute()
		# We can also pass maxResults to get any number of emails. Like this:
		# try:
		print("Fetching last {} emails".format(number_of_emails))
		# connecting to gmail API object
		gmail = build('gmail', 'v1', credentials=self.creds)
		result = gmail.users().messages().list(maxResults=number_of_emails, userId='me').execute()
		messages = result.get('messages')

		# messages is a list of dictionaries where each dictionary contains a message id.
		# iterate through all the messages
		recent_email_data = {}

		for msg_num, msg in enumerate(messages):
			# try:
				# Get the message from its id
				txt = gmail.users().messages().get(userId='me', id=msg['id']).execute()

				# Use try-except to avoid any Errors
				# Get value of 'payload' from dictionary 'txt'
				payload = txt['payload']
				headers = payload['headers']

				# Look for Subject and Sender Email in the headers
				for d in headers:
					if d['name'] == 'Subject':
						subject = d['value']
					if d['name'] == 'From':
						sender = d['value']
					if d['name'] == 'Date':
						date = d['value']
				if "[SMSForwarder]" in subject:
					# The Body of the message is in Encrypted format. So, we have to decode it.
					# Get the data and decode it with base 64 decoder.
					if "parts" in payload.keys():
						data = payload["parts"][0]["body"]["data"]
					elif "body" in payload.keys():
						data = payload["body"]["data"]
					data = data.replace("-","+").replace("_","/")
					decoded_data = base64.b64decode(data)
					soup = BeautifulSoup(decoded_data, "lxml")
					paragraphs = soup.find_all('p')

					complete_message = ""
					for para in paragraphs:
						complete_message += para.get_text(strip=True)
					recent_email_data[msg_num] = {
						"subject": subject,
						"Date": date,
						"Message": complete_message
					}
				else:
					pass
					# print("Non forwarded email from: {}".format(sender))

			# except Exception as e:
			# 	print("Error ignored when parsing: {}".format(e))
		# pprint(recent_email_data)
		return recent_email_data
		# except Exception as e:
		# 	print("Error when fetching emails: {}".format(e))


if __name__ == "__main__":
	process_obj = EmailDataProcurement()
	process_obj.start_the_push_service()
	print(process_obj.start_pubsub_communication())