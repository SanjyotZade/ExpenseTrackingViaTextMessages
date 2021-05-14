# This file has all the variable initializations

PROJECT_ID = "expensetracking-309512"
SUBSCRIPTION_ID = "firstSub"
TOPIC_ID = "expenseTopic"
PATH_TO_CRED = "key/ETkey.json"
PATH_TO_TOKEN = "key/token.json"
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/pubsub',
    'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"
]
PATH_TO_SAVE_WATCH_RESPONSE = "data/watch.json"
EMAILS_TO_PROCESS_AT_UPDATE = 10
CONSTANT_TEXT = "[SMSForwarder] New message from "
CONSTANT_PUNTUATIONS = "\n"

DATABASE_TABLE_NAME = "training_data"
DATABASE_NAME = "ExpenseTracking"

DELETE_DUPLICATE_QUERY = "DELETE FROM "+DATABASE_TABLE_NAME+" WHERE row_num IN(select row_num from(SELECT row_num, message, messageTime, phoneNumber, messageType, ROW_NUMBER() OVER (PARTITION BY message, messageTime, phoneNumber, messageType ORDER BY message desc) AS id FROM "+DATABASE_TABLE_NAME+")AS temp_table WHERE id>1);"
LAST_ROW_QUERY = "select row_num from "+DATABASE_TABLE_NAME+" order by row_num desc limit 1"


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

