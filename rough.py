# from __future__ import print_function
# from googleapiclient.discovery import build
# from google.oauth2 import service_account
#
# SCOPES = [
#     'https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/pubsub',
#     'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"
# ]
# SERVICE_ACCOUNT_FILE = "key/SAcreds.json"
#
# credentials = service_account.Credentials.from_service_account_file(
#       SERVICE_ACCOUNT_FILE, scopes=SCOPES)
# gmail = build('gmail', 'v1', credentials=credentials)
# result = gmail.users().messages().list(maxResults=5, userId='expenseserviceaccount-623@expensetracking-309512.iam.gserviceaccount.com').execute()
# messages = result.get('messages')
# print(messages)

# from google.oauth2 import service_account
#
SCOPES = ['https://www.googleapis.com/auth/gmail.labels']
SERVICE_ACCOUNT_FILE = "key/expensetracking-309512-b534db297dca.json"
#
#
# credentials = service_account.Credentials.from_service_account_file(
#         SERVICE_ACCOUNT_FILE, scopes=SCOPES)
# delegated_credentials = credentials.with_subject('zade.sanjyot@gmail.com')
# import googleapiclient.discovery
#
# sqladmin = googleapiclient.discovery.build('sqladmin', 'v1beta3', credentials=credentials)


import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

email = "expensesa@expensetracking-309512.iam.gserviceaccount.com"
me = "zade.sanjyot@gmail.com"

cred = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES, subject=email)

gmail = build('gmail', 'v1', credentials=cred)
print(gmail.users().labels().list(userId=me).execute())
   








