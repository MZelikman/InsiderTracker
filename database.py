import sqlite3
import pandas as pd


def get_connection():
     return sqlite3.connect("insider.db")

def save_transactions(df):
     connect = get_connection()
     df.to_sql("transactions", connect, if_exists="replace", index=False)
     connect.close()
    