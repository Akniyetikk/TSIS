def get_conn():
    return psycopg2.connect(**params)

"""
import psycopg2
from config import host, user, password, db_name

def get_connection():
    return psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )
"""
