def get_conn():
    return psycopg2.connect(**params)
