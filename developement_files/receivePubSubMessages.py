from __future__ import print_function
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials



# TODO(developer)
project_id = "expensetracking-309512"
subscription_id = "firstSub"
# Number of seconds the subscriber should listen for messages
timeout = None
SCOPES = ['https://www.googleapis.com/auth/pubsub']

creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('key/pubtoken.json'):
    creds = Credentials.from_authorized_user_file('key/pubtoken.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            '../key/ETcredentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('key/pubtoken.json', 'w') as token:
        token.write(creds.to_json())

