import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
load_dotenv()
HOST = os.getenv('HOST')
DATABASE = os.getenv('DATABASE')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')

def get_user_csv(user_email):
    connection_string = f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DATABASE}'

    engine = create_engine(connection_string)
    query = "SELECT subject, sender, date, body FROM user_data WHERE user = %s"
    df = pd.read_sql_query(query, engine, params=(user_email,))
    csv_data = df.to_csv(index=False)
    return csv_data

def create_db_connection(host_name, user_name, user_password, db_name):
    connection_string = f"mysql+pymysql://{user_name}:{user_password}@{host_name}/{db_name}"
    engine = create_engine(connection_string)
    return engine

def filtered_table_to_csv(engine, query, csv_file):
    try:
        df = pd.read_sql_query(query, engine) # Execute custom query
        df.to_csv(csv_file, index=False) # Save results to CSV file
        print(f"Data exported to {csv_file}")
    except Exception as e:
        print(f"Failed to export data: {str(e)}")

