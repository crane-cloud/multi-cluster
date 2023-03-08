
import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn

def initiate_terms_table(cluster_url):
    database = "metrics.db"
    # create a database connection
    conn = create_connection(database)
    """
    Query tasks by priority
    :param conn: the Connection object
    :param priority:
    :return:
    """

    data_tuple = (cluster_url,"0",)
    try:
        conn.execute(
            "INSERT INTO terms (cluster_url, current_term) VALUES (?,?);", data_tuple)
        conn.commit()
    except sqlite3.IntegrityError as e:
        # Term already initiated
        print("Terms table already initiated")
        return None
    except Exception as e:
        print(f'Error: {e}')
        return None
            
    return get_terms()

def update_term(cluster_url,term):
    print('update term record by cluster url')
    database = "metrics.db"
    conn = create_connection(database)
    # add clusters to the database
    try :
        conn.execute(
            "UPDATE terms SET current_term = ? WHERE cluster_url = ?;", (term,cluster_url))
    except Exception as e:
        print(f'Error: {e}')
        return "update failed"
    conn.commit()
    return get_terms()

def get_terms():
    database = "metrics.db"
    # create a database connection
    conn = create_connection(database)
    query = conn.execute(
        "SELECT * FROM terms")
    conn.commit()
    terms_record = query.fetchone()
    if terms_record:
        # destructure  terms
        term = {"cluster_url": terms_record[0],
                "current_term": terms_record[1]}
        return term
    else:
        return None

