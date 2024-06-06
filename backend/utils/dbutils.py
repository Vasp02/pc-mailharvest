
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import controllers


load_dotenv()
HOST = os.getenv('HOST')
DATABASE = os.getenv('DATABASE')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')




def does_accounts_table_exist():
    try:
        connection = mysql.connector.connect(host=HOST,
                                             database=DATABASE,
                                             user=USER,
                                             password=PASSWORD)
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES LIKE 'accounts';")
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result is not None
    except Error as e:
        print(f"Error: {e}")
        return False

def does_user_data_table_exist():
    try:
        connection = mysql.connector.connect(host=HOST,
                                             database=DATABASE,
                                             user=USER,
                                             password=PASSWORD)
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES LIKE 'user_data';")
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result is not None
    except Error as e:
        print(f"Error: {e}")
        return False

def create_accounts_table():
    connection = mysql.connector.connect(host=HOST,
                                         database=DATABASE,
                                         user=USER,
                                         password=PASSWORD)
    if connection.is_connected():
        cursor = connection.cursor()
        create_table_query = """
                        CREATE TABLE accounts (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            email VARCHAR(255) NOT NULL,
                            password_hash VARCHAR(255) NOT NULL,
                            password_salt VARCHAR(255) NOT NULL
                        )"""
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'accounts' created successfully.")
        cursor.close()
        connection.close()

def create_user_data_table():
    connection = mysql.connector.connect(host=HOST,
                                         database=DATABASE,
                                         user=USER,
                                         password=PASSWORD)
    if connection.is_connected():
        cursor = connection.cursor()
        create_table_query = """
                        CREATE TABLE user_data (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            user VARCHAR(255) NOT NULL,
                            subject VARCHAR(255) NOT NULL,
                            sender VARCHAR(255) NOT NULL,
                            date DATETIME NOT NULL,
                            body TEXT NOT NULL
                        )"""
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'accounts' created successfully.")
        cursor.close()
        connection.close()

def insert_user_data(email, user_email):

    connection = mysql.connector.connect(host=HOST,
                                         database=DATABASE,
                                         user=USER,
                                         password=PASSWORD)
    if connection.is_connected():
        cursor = connection.cursor()
        insert_query = """
                            INSERT INTO user_data (user, subject, sender, date, body)
                            VALUES (%s, %s, %s, %s, %s)"""
        data_tuple = (user_email, email['subject'], email['sender'], email['date'], email['body'])
        try:
            cursor.execute(insert_query, data_tuple)
            connection.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            connection.close()


def save_account(email, password_hash, password_salt):
    try:
        connection = mysql.connector.connect(
            host=HOST,
            database=DATABASE,
            user=USER,
            password=PASSWORD
        )

        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            cursor = connection.cursor()

            insert_query = """INSERT INTO accounts (email, password_hash, password_salt) VALUES (%s, %s, %s)"""
            record = (email, password_hash, password_salt)
            cursor.execute(insert_query, record)
            connection.commit()

            print("Record inserted successfully into accounts table")

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

def account_exists(email):
    try:
        connection = mysql.connector.connect(host=HOST,
                                             database=DATABASE,
                                             user=USER,
                                             password=PASSWORD)
        if connection.is_connected():
            with connection.cursor() as cursor:
                query = "SELECT * FROM accounts WHERE email = %s"
                cursor.execute(query, (email,))
                result = cursor.fetchone()
                return result is not None
    except Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if connection.is_connected():
            connection.close()


def delete_all_user_data(user_email):
    connection = mysql.connector.connect(host=HOST,
                                         database=DATABASE,
                                         user=USER,
                                         password=PASSWORD)
    if connection.is_connected():
        cursor = connection.cursor()
        delete_query = """
                            DELETE FROM user_data WHERE user = %s"""
        cursor.execute(delete_query, (user_email,))
        connection.commit()
        print("All user data deleted successfully.")
        cursor.close()
        connection.close()

def does_account_filters_table_exist():
    try:
        connection = mysql.connector.connect(host=HOST,
                                             database=DATABASE,
                                             user=USER,
                                             password=PASSWORD)
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES LIKE 'account_filters';")
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result is not None
    except Error as e:
        print(f"Error: {e}")
        return False

def create_account_filters_table():
    connection = mysql.connector.connect(host=HOST,
                                         database=DATABASE,
                                         user=USER,
                                         password=PASSWORD)
    if connection.is_connected():
        cursor = connection.cursor()
        create_table_query = """
                        CREATE TABLE account_filters (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            user VARCHAR(255) NOT NULL,
                            password VARCHAR(255) NOT NULL,
                            subject VARCHAR(255),
                            sender VARCHAR(255),
                            receiver VARCHAR(255),
                            words_in_body TEXT,
                            date_from DATETIME,
                            date_to DATETIME
                        )"""
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'account_filters' created successfully.")
        cursor.close()
        connection.close()

def insert_new_account_filter(email, password, criteria):
    connection = mysql.connector.connect(host=HOST,
                                         database=DATABASE,
                                         user=USER,
                                         password=PASSWORD)
    subject = criteria.subject
    sender = criteria.sender
    reciever = criteria.receiver
    words_in_body = criteria.words_in_body
    date_from = criteria.date_from
    date_to = criteria.date_to

    if connection.is_connected():
        cursor = connection.cursor()
        insert_query = """
                INSERT INTO account_filters (user, password, subject, sender, receiver, words_in_body, date_from, date_to)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
        data_tuple = (email, password, subject, sender, reciever, words_in_body, date_from, date_to)
        cursor.execute(insert_query, data_tuple)
        connection.commit()
        print("Data inserted successfully.")
        cursor.close()
        connection.close()

def get_all_filters_for_account(email):
    connection = mysql.connector.connect(host=HOST,
                                         database=DATABASE,
                                         user=USER,
                                         password=PASSWORD)
    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)
        select_query = """
            SELECT id, user, subject, sender, receiver, words_in_body, date_from, date_to
            FROM account_filters
            WHERE user = %s
        """
        cursor.execute(select_query, (email,))
        filters = cursor.fetchall()
        cursor.close()
        connection.close()
        return filters

def delete_account_filter_by_id(filter_id):
    try:
        connection = mysql.connector.connect(host=HOST,
                                             database=DATABASE,
                                             user=USER,
                                             password=PASSWORD)
        if connection.is_connected():
            cursor = connection.cursor()

            # Delete related rows from filter_scrapes table
            delete_filter_scrapes_query = "DELETE FROM filter_scrapes WHERE filter_id = %s"
            cursor.execute(delete_filter_scrapes_query, (filter_id,))

            # Delete the row from account_filters table
            delete_account_filter_query = "DELETE FROM account_filters WHERE id = %s"
            cursor.execute(delete_account_filter_query, (filter_id,))

            connection.commit()
            print(f"Filter with ID {filter_id} and related scrapes deleted successfully.")

            cursor.close()

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            connection.close()
            print("MySQL connection is closed")


def get_filter_id_owner(filter_id):
    try:
        connection = mysql.connector.connect(host=HOST,
                                             database=DATABASE,
                                             user=USER,
                                             password=PASSWORD)
        if connection.is_connected():
            cursor = connection.cursor()

            # Query to get the owner (user) of the filter by its ID
            query = "SELECT user FROM account_filters WHERE id = %s"
            cursor.execute(query, (filter_id,))

            # Fetch the result
            result = cursor.fetchone()

            # If a result is found, return the owner, else return None
            if result:
                return result[0]
            else:
                return None

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            connection.close()
            print("MySQL connection is closed")



def does_filter_scrapes_table_exist():
    try:
        connection = mysql.connector.connect(host=HOST,
                                             database=DATABASE,
                                             user=USER,
                                             password=PASSWORD)
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES LIKE 'filter_scrapes';")
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result is not None
    except Error as e:
        print(f"Error: {e}")
        return False

def create_filter_scrapes_table():
    connection = mysql.connector.connect(host=HOST,
                                         database=DATABASE,
                                         user=USER,
                                         password=PASSWORD)
    if connection.is_connected():
        cursor = connection.cursor()
        create_table_query = """
                        CREATE TABLE filter_scrapes (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            subject VARCHAR(255),
                            sender VARCHAR(255),
                            date DATETIME,
                            body TEXT,
                            filter_id INT,
                            FOREIGN KEY (filter_id) REFERENCES account_filters(id)
                        )"""
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'account_filters' created successfully.")
        cursor.close()
        connection.close()

def insert_filter_scrape_data(subject, sender, date, body, filter_id):

    connection = mysql.connector.connect(host=HOST,
                                         database=DATABASE,
                                         user=USER,
                                         password=PASSWORD)

    if connection.is_connected():
        cursor = connection.cursor()
        insert_query = """
                                    INSERT INTO filter_scrapes (subject, sender, date, body, filter_id)
                                    VALUES (%s, %s, %s, %s, %s)"""
        data_tuple = (subject, sender, date, body, filter_id)
        cursor.execute(insert_query, data_tuple)
        connection.commit()
        print("Data inserted successfully.")
        cursor.close()
        connection.close()

def get_acct_filter_row_by_id(row_id):
    connection = mysql.connector.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD)
    try:
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            select_query = "SELECT * FROM account_filters WHERE id = %s"
            cursor.execute(select_query, (row_id,))
            row = cursor.fetchone()
            if row:
                return row
            else:
                return "No row found with id {}".format(row_id)
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()


def get_scrapes_of_filter_id(filter_id):
    print('monitor working')
    connection = mysql.connector.connect(host=HOST,
                                         database=DATABASE,
                                         user=USER,
                                         password=PASSWORD)
    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)
        select_query = "SELECT * FROM filter_scrapes WHERE filter_id = %s"
        cursor.execute(select_query, (filter_id,))
        rows = cursor.fetchall()

        for row in rows:
            print(f"row : {row}")

        cursor.close()
        connection.close()
        return rows
    else:
        print("Failed to connect to the database.")
        return[]



def monitor_user_filters():
    print('[MONITOR] : monitoring')
    connection = mysql.connector.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD)
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM account_filters")

        while True:
            row = cursor.fetchone()
            if row is None:
                break
            controllers.scrape_controller.process_filter(row)

    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()




