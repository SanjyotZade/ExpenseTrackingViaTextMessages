# This file has all the variable initializations

# process variables
EMAIL = "epochs.ai@sanjyot.info"
PROJECT_ID = "expensetra"
SUBSCRIPTION_ID = "expenseTopic-sub"
TOPIC_ID = "expenseTopic"
PATH_TO_CRED = "/home/sj-ai-lsb/Documents/keys/ExpenseTrackingViaTextMessages/expenseTrackingServiceKey.json"
PATH_TO_TOKEN = "key/token.json"
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/pubsub',
    'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"
]
PATH_TO_SAVE_WATCH_RESPONSE = "/home/sj-ai-lsb/Documents/keys/ExpenseTrackingViaTextMessages/watch.json"
EMAILS_TO_PROCESS_AT_UPDATE = 10
CONSTANT_TEXT = "[SMSForwarder] New message from "
CONSTANT_PUNTUATIONS = "\n"

# csv variables
PATH_TO_ENTIRE_SMS_CSV = "/home/sj-ai-lsb/Documents/data/ExpenseTrackingViaTextMessages/expenseSMSData.csv"
PATH_TO_ENTIRE_TRAS_SMS_CSV = "/home/sj-ai-lsb/Documents/data/ExpenseTrackingViaTextMessages/expenseTrasData.csv"

# data base variables
DATABASE_TABLE_NAME = "training_data"
DATABASE_NAME = "ExpenseTracking"
DELETE_DUPLICATE_QUERY = "DELETE FROM "+DATABASE_TABLE_NAME+" WHERE row_num IN(select row_num from(SELECT row_num, message, messageTime, phoneNumber, messageType, ROW_NUMBER() OVER (PARTITION BY message, messageTime, phoneNumber, messageType ORDER BY message desc) AS id FROM "+DATABASE_TABLE_NAME+")AS temp_table WHERE id>1);"
LAST_ROW_QUERY = "select row_num from "+DATABASE_TABLE_NAME+" order by row_num desc limit 1"

# Spreadsheet variables
SHEET_NAME = "FinanceManagement"
WORK_BOOK_NAME = "Expense21-22"
# SHEET_NAME = "to_purcase"
# WORK_BOOK_NAME = "general"
WIDTH_OF_WBSHEET_DATA = 7
COL_HEADERS_DICT= {
    2: "Month",
    3: "Category",
    4: "Description",
    5: "Amount",
    6: "Amount_pred",
    7: "Message"
}

