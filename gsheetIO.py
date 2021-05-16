from __future__ import print_function
import string
import os.path
import gspread
from config import *
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


class GsheetIO:

    def __init__(self, creds=None):

        # authorize the clientsheet
        client = gspread.authorize(creds)

        # get the instance of the Spreadsheet
        self.sheet = client.open(SHEET_NAME)

        list_of_alpha = [alpha for alpha in string.ascii_uppercase]
        self.alpha_dict = dict(zip(range(1, len(list_of_alpha)), list_of_alpha))

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
    def next_available_row(worksheet, col_num):
        str_list = list(filter(None, worksheet.col_values(col_num)))
        return len(str_list) + 1

    def update_expense_sheet(self, input_data):
        col_row_start = (2, 1)
        # get the first sheet of the Spreadsheet
        sheet_instance = self.sheet.worksheet(WORK_BOOK_NAME)
        row_num = self.next_available_row(sheet_instance, col_row_start[0])
        start_col = self.alpha_dict[col_row_start[0]]
        row_start = row_num
        end_col = self.alpha_dict[col_row_start[0]+(WIDTH_OF_WBSHEET_DATA-1)]
        row_end = row_start+(len(input_data)-1)
        cell_range = "{}{}:{}{}".format(start_col, row_start, end_col, row_end)
        sheet_instance.update(cell_range, input_data)
        print("Expense sheet updated with {} entries".format(len(input_data)))
        return


if __name__ == "__main__":
    gsheet_obj = GsheetIO()
    gsheet_obj.update_expense_sheet([[1,2,3,4,5,6],[7,8,9,10,11,12]])



