import re
import time
#from Sql import Sql
import pandas as pd
from gsheetIO import GsheetIO
from datetime import datetime
from config import DATABASE_NAME
from config import CONSTANT_TEXT
from config import LAST_ROW_QUERY
from config import DATABASE_TABLE_NAME
from config import CONSTANT_PUNTUATIONS
from config import DELETE_DUPLICATE_QUERY
from config import PATH_TO_ENTIRE_SMS_CSV
from config import PATH_TO_ENTIRE_TRAS_SMS_CSV


class DataPreparation:

    def __init__(self, creds=None):
        self.gsheet_obj = GsheetIO(creds=creds)

    @staticmethod
    def data_pre_processing(email_data):
        email_data_updated = {}
        for email_num, email_info in email_data.items():
            subject_info = email_info['subject']
            subject_info = subject_info.replace(CONSTANT_TEXT, "")
            sender_name, date_time = subject_info.split(" - ")
            email_info["Message"] = email_info["Message"].replace("\r", "")
            message = " ".join((email_info["Message"].split(CONSTANT_PUNTUATIONS))[1:])
            now = datetime.now()

            date_time = datetime.strptime(date_time+" "+str(now.year), '%m/%d, %I:%M %p %Y').strftime('%d %b %Y %I:%M')
            email_data_updated[email_num] = {
                'row_num': None,
                'phoneNumber': sender_name,
                'messageType': "Received",
                'message': message,
                'messageTime': date_time
            }
        return email_data_updated

    def update_to_database(self, email_data):
        if email_data is not None:
            email_data_updated = self.data_pre_processing(email_data)
            last_rows = self.sql_obj.execute_view_query("select count(*) from {}".format(DATABASE_TABLE_NAME))[0][0]
            for email_num, email_info in email_data_updated.items():
                row = self.sql_obj.execute_view_query(LAST_ROW_QUERY)[0][0]+1
                self.sql_obj.insert_to_table(
                    table_name=DATABASE_TABLE_NAME,
                    column_names=['row_num', 'phoneNumber', 'messageType', 'message', 'messageTime', 'trans', 'amounts'],
                    row_data=[
                        (
                            row,
                            email_info["phoneNumber"],
                            email_info["messageType"],
                            email_info["message"],
                            email_info["messageTime"],
                            str(self.find_trans_msg(email_info["message"])),
                            str(self.extract_amounts(email_info["message"]))
                         )
                    ]
                )
            self.sql_obj.execute_update_query(DELETE_DUPLICATE_QUERY)
            print("Waiting for 2 sec..")
            time.sleep(2)
            recent_rows = self.sql_obj.execute_view_query("select count(*) from {}".format(DATABASE_TABLE_NAME))[0][0]
            if recent_rows > last_rows:
                print("{} database rows updated successfully".format(recent_rows-last_rows))
                return self.sql_obj.execute_view_query("select * from {} order by row_num desc limit {}".format(DATABASE_TABLE_NAME, (recent_rows-last_rows)))
            else:
                print("SMS data already up to date in the database")
                return
        else:
            print("Email data: {}".format(email_data))
            return

    def update_to_csv(self, email_data):
        sms_data = pd.read_csv(PATH_TO_ENTIRE_SMS_CSV)
        if email_data is not None:
            email_data_updated = self.data_pre_processing(email_data)
            last_rows = sms_data.shape[0]
            row = int(sms_data.loc[last_rows-1, "row_num"])+1
            current_email_data = []

            for email_num, email_info in email_data_updated.items():
                column_names = ['row_num', 'phoneNumber', 'messageType', 'message', 'messageTime', 'trans', 'amounts']
                row_data = [
                        row+1,
                        email_info["phoneNumber"],
                        email_info["messageType"],
                        email_info["message"],
                        email_info["messageTime"],
                        str(self.find_trans_msg(email_info["message"])),
                        str(self.extract_amounts(email_info["message"]))
                ]
                current_email_data.append(dict(zip(column_names, row_data)))
                row += 1
            sms_data = sms_data.append(current_email_data, ignore_index=True)
            sms_data = sms_data.drop_duplicates(subset=['phoneNumber', 'messageType', 'message', 'messageTime', 'trans', 'amounts'])
            recent_rows = sms_data.shape[0]
            if recent_rows > last_rows:
                print("{} data rows updated successfully".format(recent_rows-last_rows))
                sms_data.to_csv(PATH_TO_ENTIRE_SMS_CSV, index=False)
                return sms_data.iloc[-(recent_rows-last_rows):, ]
            else:
                print("SMS data already up to date in the database")
                return
        else:
            print("Email data: {}".format(email_data))
            return

    @staticmethod
    def covert_to_float(num):
        return round(float(num), 1)

    def update_expense_excel(self, updated_rows):
        if updated_rows is not None:
            exp_amt = None
            update_row_processed = []
            updated_rows.reset_index(inplace=True)
            for row_num, trans in enumerate(updated_rows["trans"]):
                trans_words = eval(trans)

                if trans_words:
                    amounts = eval(updated_rows.loc[row_num, "amounts"])
                    if amounts:
                        if len(amounts) > 1:
                           for amt in amounts:
                               if not amt[1]:
                                  exp_amt = self.covert_to_float(amt[0][0])
                                  break
                        if exp_amt is None:
                           exp_amt = self.covert_to_float(amounts[0][0][0])
                    else:
                        exp_amt = self.covert_to_float(0)

                    if (("credited" in trans_words) or ("refund" in trans_words)) and ("debited" not in trans_words):
                        exp_amt *= -1

                    month = datetime.strptime(updated_rows.loc[row_num, "messageTime"], '%d %b %Y %I:%M').strftime('%B')
                    message = updated_rows.loc[row_num, "message"]
                    row_num = str(updated_rows.loc[row_num, "row_num"])
                    update_row_processed.append([month, "", "", exp_amt, exp_amt, message, row_num])
                    exp_amt = None

            if update_row_processed:
                self.gsheet_obj.update_expense_sheet(update_row_processed)
        return

    @staticmethod
    def find_trans_msg(x):
        x = x.lower()
        keywords = ["credited", "debited", "refund",  "txn", "transaction", "tx#", "payment"] #"sbi", "icici", "hdfc", "balance", "bal"
        x = [key for word in x.split() for key in keywords if word.find(key)>=0]
        if x:
            return x
        else:
            return False

    @staticmethod
    def extract_numbers(x):
        return str([int(s) for s in x.split() if s.isdigit()])

    @staticmethod
    def amount_if_balance(words):
        for word in words:
            word = word.lower()
            if (word.find("bal") >= 0) or (word.find("balance") >= 0):
                return True
        return False

    def extract_amounts(self, x):
        keywords = ["inr", "rs"]
        x_splited = x.split()
        amounts = []
        res = False
        bal = False
        for w_num, w in enumerate(x_splited):
            for kword in keywords:
                w_ = w.lower()
                if w_.find(kword) >= 0:

                    # if kword == w_:
                    #     exact =True

                    w_ = w_.replace(' ', '')
                    w_ = w_.replace(kword+".", '')
                    w_ = w_.replace(kword, '')
                    w_ = w_.replace(",", '')

                    res_2 = re.findall(r"[-+]?\d*\.\d+|\d+", w_)
                    if w_num !=0:
                        res_1_temp = x_splited[w_num-1].replace(' ', '')
                        res_1_temp = res_1_temp.replace(',', '')

                        res_1 = re.findall( r"[-+]?\d*\.\d+|\d+",  res_1_temp)
                        # print("#########", x_splited[w_num - 1], res_1)
                    else:
                        # print("SOL")
                        res_1_temp = ""
                        res_1 = ""

                    # print("#########", w_, res_2)

                    if w_num != len(x_splited)-1:
                        res_3_temp = x_splited[w_num + 1].replace(' ', '')
                        res_3_temp = res_3_temp.replace(',', '')

                        res_3 = re.findall( r"[-+]?\d*\.\d+|\d+",  res_3_temp)
                        # print("#########", x_splited[w_num + 1], res_3)
                    else:
                        # print("EOL")
                        res_3_temp = ""
                        res_3 = ""

                    bal = self.amount_if_balance([w_, res_3_temp, res_1_temp])

                    if len(res_2) > 0:
                        res = (res_2)

                    elif len(res_3) > 0:
                        res = (res_3)

                    elif len(res_1) > 0:
                        res = (res_1)
                    else:
                        res = False
            if res:
                amounts.append((res, bal))
                res = False
        return amounts


if __name__ == "__main__":
    data_prep_obj = DataPreparation()
    data = {0: {'Date': 'Sat, 3 Apr 2021 09:38:02 -0700',
         'Message': 'From:Â\xa0AM-TFAROT\r\n'
                    'Pack Valid till Jun 16 2021. Remaining SMS:893.00 '
                    'Bal:Rs.8.90.',
         'subject': '[SMSForwarder] New message from AM-TFAROT - 04/03 PM 10:07'},
     1: {'Date': 'Sat, 3 Apr 2021 09:37:58 -0700',
         'Message': 'From:Â\xa0+918983383349(RadhaağŸ‘»)\r\nHi',
         'subject': '[SMSForwarder] New message from +918983383349(Radhaa👻) - '
                    '04/03 PM 10:07'},
     4: {'Date': 'Sat, 3 Apr 2021 07:33:35 -0700',
         'Message': 'From:Â\xa0JM-620016\r\n'
                    'Plan expired! Recharge Now using Google Pay app for Jio no. '
                    '7400108949 with Rs.149 Plan & enjoy unlimited voice and data. '
                    'Click www.jio.com/r/puwzGxD1c',
         'subject': '[SMSForwarder] New message from JM-620016 - 04/03 PM 8:03'},
     9: {'Date': 'Sat, 3 Apr 2021 04:59:25 -0700',
         'Message': 'From:Â\xa0+918983383349(RadhaağŸ‘»)\r\n'
                    'Could not see earlier message',
         'subject': '[SMSForwarder] New message from +918983383349(Radhaa👻) - '
                    '04/03 PM 5:29'},
     10: {'Date': 'Sat, 3 Apr 2021 04:58:49 -0700',
          'Message': 'From:Â\xa0AM-TFAROT\r\n'
                     'Pack Valid till Jun 16 2021. Remaining SMS:895.00 '
                     'Bal:Rs.8.80.',
          'subject': '[SMSForwarder] New message from AM-TFAROT - 04/03 PM 5:28'},
     11: {'Date': 'Sat, 3 Apr 2021 04:58:46 -0700',
          'Message': 'From:Â\xa0+918983383349(RadhaağŸ‘»)\r\nğŸ˜˜',
          'subject': '[SMSForwarder] New message from +918983383349(Radhaa👻) - '
                     '04/03 PM 5:28'},
     12: {'Date': 'Sat, 3 Apr 2021 04:57:19 -0700',
          'Message': 'From:Â\xa0AM-TFAROT\r\n'
                     'Pa i till debited Jun 16 2021. RemSS:9.00 '
                     'Bal:Rs.98.80.',
          'subject': '[SMSForwarder] New message from AM-TFAROT - 04/03 PM 5:27'},
     13: {'Date': 'Sat, 3 Apr 2021 04:57:16 -0700',
          'Message': 'From:Â\xa0+918983383349(RadhaağŸ‘»)\r\nHi',
          'subject': '[SMSForwarder] New mesage fm +91898338349(Radhaa👻) - '
                     '04/03 PM 5:27'},
     14: {'Date': 'Sat, 3 Apr 2021 04:53:24 -0700',
          'Message': 'From:Â\xa0AM-TFAROT\r\n'
                     'Vli     21. Credited Remn SMS:9.00 '
                     'Bal:Rs.8.8 BAL INR 58 BAL',
          'subject': '[SMSForwarder] New message fro AM-TFAROT - 04/03 PM 5:23'}}

    x = data_prep_obj.update_to_csv(data)
    data_prep_obj.update_expense_excel(x)
    print(x)
    # import pandas as pd
    # # from the CSV file
    # # path_to_csv_file = "./data/sms_backup_3032021.csv"
    # # sms_data = pd.read_csv(path_to_csv_file)
    # # print(sms_data.columns.values)
    # # [print(sms+"\n") for sms in sms_data["message"]]
    #
    # data_prep_obj = DataPreparation(connect_db=True)
    #
    # messages = data_prep_obj.sql_obj.execute_view_query("select message, row_num from sms_data_original_live")
    #
    # message_updated = [(x[1], str(data_prep_obj.find_trans_msg(x[0])), str(data_prep_obj.extract_amounts(x[0]))) for x in messages]
    #
    # # print(message_updated[:5])
    # data_prep_obj.sql_obj.insert_to_table("temp_tb", ["row_num", "trans", "amounts"], message_updated)
    #
    # # message_updated = messages.apply(lambda x: data_prep_obj.data_prep(x))
    # # for i in range(len(messages)):
    # #     print(i, message_updated[i], messages[i], "\n")
    # #     if i == 100:
    # #         break
    # # sms_data['amounts'] = sms_data['message'].apply(lambda x: data_prep_obj.extract_amounts(x))
    #
    # # sms_data_sub = sms_data[sms_data["transaction"]==True]
    # # show_wordcloud(sms_data_sub['message'])
    # [print(trans_sms+"\n") for trans_sms in sms_data_sub['message']]

