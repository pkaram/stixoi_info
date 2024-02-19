"""
utility functions to conncet to db and make http requests
"""
import logging
import sqlite3
import requests
import pandas as pd

DB_NAME = 'stixoi_info.db'
logging.getLogger().setLevel(logging.INFO)

def store_df_to_db(df, table_name, strategy='replace'):
    "stores dataframe to database"
    try:
        cnx = sqlite3.connect(DB_NAME)
        df.to_sql(name=table_name, con=cnx, index=False, if_exists=strategy)
        return df
    except Exception as e:
        logging.info('error while connecting to db: %s',e)
        return None
    finally:
        cnx.close()


def get_data_from_db(query):
    "gets data from database into a dataframe"
    try:
        cnx = sqlite3.connect(DB_NAME)
        df = pd.read_sql(query, cnx)
        return df
    except Exception as e:
        logging.info('error while connecting to db: %s',e)
    finally:
        cnx.close()

def make_request(url):
    "makes http request"
    try:
        r = requests.get(url, verify=False, timeout=3)
        r.raise_for_status()
        return r
    except requests.exceptions.HTTPError as e:
        logging.info("Http Error: %s", e)
    except requests.exceptions.ConnectionError as e:
        logging.info("Error Connecting: %s", e)
    except requests.exceptions.Timeout as e:
        logging.info("Timeout Error: %s", e)
    except requests.exceptions.RequestException as e:
        logging.info("OOps: Something Else: %s", e)
