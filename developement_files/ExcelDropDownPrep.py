import os
import string
import pandas as pd
import xlsxwriter


def convert_csv_to_excel(path_to_csv, name_of_excel="output.xlsx", name_of_the_excel_sheet="mysheet"):
    csv_folder, csv_name = os.path.split(path_to_csv)
    # read the csv into a pandas dataframe
    data = pd.read_csv(path_to_csv)

    # setup the write
    path_to_save_excel = os.path.join(csv_folder, name_of_excel)
    writer = pd.ExcelWriter(path_to_save_excel, engine='xlsxwriter')

    # write the dataframe to an xlsx file
    data.to_excel(writer, sheet_name=name_of_the_excel_sheet, index=False)
    writer.save()
    return


def if_else(x):
    x = eval(x)
    if x:
        return True
    else:
        return False


if __name__ == "__main__":
    path = '/data/transaction_mapped.csv'

    categories = [
    "Other_bills",
    "Food",
    "Shopping",
    "Entertainment",
    "Fuel",
    "Travel",
    "Others",
    "Rent",
    "Maid",
    "PuneElectric",
    "BpurElectric",
    "BpurWater",
    ]

    sms_data = pd.read_csv(path)
    sms_data["amounts_"]  = ""
    sms_data["transaction_"] = False
    sms_data["category"] = ""
    sms_data["transaction_"] = sms_data["transaction"].apply(lambda x: if_else(x))
    sms_data_columns = sms_data.columns.values

    list_of_alpha = [ alpha for alpha in string.ascii_uppercase]
    alpha_dict = dict(zip( range(len(list_of_alpha)), list_of_alpha))
    workbook = xlsxwriter.Workbook('../data/traning_data_batch2.xlsx')
    worksheet = workbook.add_worksheet()

    for num, alpha in alpha_dict.items():
        worksheet.set_column(alpha+':'+alpha)
    worksheet.set_row(0, sms_data.shape[1])

    for row_num, msg in enumerate(sms_data["message"]):
        if row_num > 4001:
            row_num_temp = row_num
            row_num = row_num - 4001
            for col_num, col in enumerate(sms_data_columns):
                if col not in ["amounts_", "transaction_", "category"]:
                    worksheet.write(row_num, col_num, sms_data.loc[row_num_temp][col_num])
                elif col == "amounts_":
                    amount_list = eval(sms_data.iloc[row_num_temp]["amounts"])
                    amounts = [x[0][0] for x in amount_list]
                    worksheet.data_validation(alpha_dict[col_num]+str(row_num+1), {'validate': 'list', 'source': amounts})
                elif col == "transaction_":
                    worksheet.data_validation(alpha_dict[col_num]+str(row_num+1), {'validate': 'list', 'source': [True, False]})
                elif col == "category":
                    worksheet.data_validation(alpha_dict[col_num]+str(row_num+1), {'validate': 'list', 'source': categories})
                else:
                    print("Should not be here")

    workbook.close()