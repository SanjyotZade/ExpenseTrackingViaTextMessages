import mysql.connector


class Sql:

    def __init__(self, db_name=None, host_name="127.0.0.1", user_name="root", password="password123"):
        """
        This function is used establish connection with MySQL server or MySQL database.
        Args:
            db_name{str}:  Name of the database(optional)
            host_name{str}: Hostname where MySQL server is hosted.
            user_name{str}: Username for the hosting machine.
            password{str}: Passowrd for the user_name in  the hosting machine.
        """

        if db_name is not None:
            self.myserver = mysql.connector.connect(
                host=host_name,
                user=user_name,
                db=db_name,
                passwd=password,
            )
        else:
            self.myserver = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=password,
            )

        if self.myserver:
            print("Connection to database successful\n")
        else:
            print("Couldn't establish connection to the database\n")

    def create_db(self, db_name):
        """
        This method can be used to create a new db.
        Args:
            db_name: Name of the new database to be created.

        Returns: None

        """
        cursor = self.myserver.cursor()
        command = "CREATE DATABASE {}".format(db_name)
        cursor.execute(command)
        return

    def show_databases(self):
        """
        This method can be used to view all the databases in the MySQL in the current host.
        Returns: None
        """
        cursor =self.myserver.cursor()
        command = "SHOW DATABASES"
        cursor.execute(command)
        for db in cursor:
            print(db)
        return

    def show_tables(self, db_name=None):
        """
        This method can be used to view all the tables in the MySQL in the current host.
        Args:
            db_name: Name of the database for which the tables have to be viewed.
        Returns: None
        """
        if self.myserver.database is not None:
            pass
        elif db_name is not None:
            self.myserver.database = db_name
        else:
            print("Please specify the database_name in the object definition or as parameter")
            return

        cursor = self.myserver.cursor()
        command = "SHOW TABLES"
        cursor.execute(command)
        for table in cursor:
            print(table)
        return

    def create_table(self, table_name, variable_definitions, db_name=None):
        """
        This method can be used to create tables in a mentioned database.
        Args:
            table_name{str}: Name of the new table to be created.
            variable_definitions{list}: Definitions of each columns in the table to be created.
            Example. ["id int(20)", "names varchar(200)"]
            db_name{str}: Name of the database where the table should be created.

        Returns:

        """

        if self.myserver.database is not None:
            pass
        elif db_name is not None:

            self.myserver.database = db_name
        else:
            print("Please specify the database_name in the object definition or as parameter")
            return

        cursor = self.myserver.cursor()
        command = "CREATE TABLE {} ( ".format(table_name)

        for var_num, var in enumerate(variable_definitions):
            if not var_num == len(variable_definitions) - 1:
                command = command + var + ", "
            else:
                command = command + var + ")"
        cursor.execute(command)
        return

    def insert_to_table(self, table_name, column_names, row_data, db_name=None):
        """
        This function can be use to insert a row in the database table.
        Args:
            table_name: Name of the table where the row is to be inserted
            column_names: Name of the columns where the row_data is to be inserted
            Example 1. ["Id", "Names"] or Example 2. ["Names"]
            row_data: Row data to be inserted in the table
            Example 1. [(1, "Sam"), (2, "Max")] or Example 2. ["Sam"] Respectively w.r.t to above example
            db_name: Name of the database where the data is to be inserted
        Note: To enter multiple value to single column use for loop(with example 2 was base command).
        Returns:

        """
        if self.myserver.database is not None:
            pass
        elif db_name is not None:
            self.myserver.database = db_name
        else:
            print("Please specify the database_name in the object definition or as parameter")
            return
        cursor = self.myserver.cursor()
        command = "INSERT INTO {}(".format(table_name)
        for col_num, col_name in enumerate(column_names):
            if col_num != len(column_names)-1:
                command = command + col_name+","
            else:
                command = command + col_name+") "
        num_columns = len(column_names)
        command += "VALUES("
        for i in range(num_columns):
            if i != num_columns-1:
                command += "%s,"
            else:
                command += "%s)"

        if num_columns < 1:
            print("Mention altleast one column")
        elif num_columns == 1:
            cursor.execute(command, row_data)
        else:
            cursor.executemany(command, row_data)

        self.myserver.commit()
        return

    def execute_view_query(self, query, db_name=None):
        """
        This method can be user to execute view query.
        Args:
            query: Query to execute.
            db_name: Name of the databse if not specified in the class object.

        Returns:
            All the fetched results to view
        """
        if self.myserver.database is not None:
            pass
        elif db_name is not None:
            self.myserver.database = db_name
        else:
            print("Please specify the database_name in the object definition or as parameter")
            return

        cursor = self.myserver.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        return result

    def execute_update_query(self, query, db_name=None):
        """
        This method can be used to update the value in the database table based on an input query.
        Args:
            query: Query to execute.
            db_name: Name of the databse if not specified in the class object.

        Returns:
            None
        """
        if self.myserver.database is not None:
            pass
        elif db_name is not None:
            self.myserver.database = db_name
        else:
            print("Please specify the database_name in the object definition or as parameter")
            return
        cursor = self.myserver.cursor()
        cursor.execute(query)
        self.myserver.commit()
        return


if __name__ == "__main__":
    sql_obj = Sql(db_name="ExpenseTracking", password="Tinku786$")

    # row = sql_obj.execute_view_query("select row_num from sms_data_original_live order by row_num desc limit 1")
    # row = row[0][0]+1
    # print(row)
    # for i in range(3):
    #     sql_obj.insert_to_table(
    #         table_name="sms_data_original_live",
    #         column_names=['row_num', 'phoneNumber', 'messageType', 'message', 'messageTime'],
    #         row_data=[(row+i, "x", "x", "x", "x")]
    #     )
    # rough
    # sql_obj.create_table(table_name="testing_new", variable_definitions=["one varchar(30)", "two int(30)"])
    # sql_obj.insert_to_table(table_name="testing_new", column_names=["two"], row_data=[100])
    # sql_obj.execute_update_query("UPDATE testing_new SET one = 'NEWHundred' WHERE two=100")
    # sql_obj.execute_update_query("UPDATE testing_new SET one = 'Nighty eight' WHERE two=98")
    # sql_obj.execute_update_query("DELETE FROM testing_new WHERE one='Sanjyot'")
    #
    # data = sql_obj.execute_view_query("SELECT * FROM testing_new")
    # for val in data:
    #     print(val)

