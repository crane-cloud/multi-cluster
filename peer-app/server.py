from jsonrpcserver import Success, method, serve,  InvalidParams, Result, Error
from datetime import datetime
import sqlite3
from sqlite3 import Error
import re
import json
import os
from discovery import check_cluster_info
from terms import initiate_terms_table, get_terms, update_term
from metrics import getCPU, getMemory, getDisk

@method
def check_availability() -> Result:
    result = {"data": "Cluster on", "message": "success", "status": 200}

    return Success(result)

@method
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

@method
def get_server_resources() -> Result:
    cpu = getCPU()
    memory = getMemory()
    disk = getDisk()

    resources = {"cpu":cpu, "memory": memory, "disk":disk}

    if resources:
        result = {"data": resources, "message": "success", "status": 201}
    else:
        result = {"data": Error, "message": "failed", "status": 500}

    return Success(result)

@method
def select_all_network_metrics() -> Result:
    database = "metrics.db"

    # create a database connection
    conn = create_connection(database)
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM network")

    rows = cur.fetchall()

    for row in rows:
        print(row)
    if rows:
        result = {"network data": rows, "message": "success", "status": 201}
    else:
        result = {"network data": Error, "message": "failed", "status": 500}

    return Success(result)

@method
def select_metrics_by_cluster(cluster_id, metric_type) -> Result:
    database = "metrics.db"

    # create a database connection
    conn = create_connection(database)
    """
    Query tasks by priority
    :param conn: the Connection object
    :param priority:
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM "+metric_type +
                " WHERE cluster_id=?", (cluster_id,))

    rows = cur.fetchall()

    for row in rows:
        print(row)

    if rows:
        result = {"data": rows, "message": "success", "status": 201}
    else:
        result = {"data": Error, "message": "failed", "status": 500}

    return Success(result)

@method
def insert_network(metrics) -> Result:
    database = "metrics.db"
    # create a database connection
    conn = create_connection(database)
    # Use executemany() to insert multiple records at a time
    query = conn.execute(
        "INSERT INTO network (cluster_id,throughput,latency, jitter, date) VALUES (?,?,?,?,?)", metrics)

    for row in conn.execute('SELECT * FROM network'):
        print(row)
    conn.commit()

    if query:
        return Success(True)
    else:
        return Success(False)

@method
def insert_availability(metrics) -> Result:
    database = "metrics.db"
    # create a database connection
    conn = create_connection(database)
    # Use executemany() to insert multiple records at a time
    query = conn.execute(
        "INSERT INTO availability (cluster_id,availability_score,date) VALUES (?,?,?)", metrics)

    for row in conn.execute('SELECT * FROM network'):
        print(row)
    conn.commit()

    if query:
        return Success(True)
    else:
        return Success(False)


def create_table(conn):
    try:
        # Cluster information table
        create_cluster_info_table_query = '''CREATE TABLE IF NOT EXISTS cluster_info (
                                    cluster_id TEXT PRIMARY KEY,
                                    name TEXT NOT NULL,
                                    ip_address TEXT NOT NULL,
                                    port INTEGER NOT NULL);
                                    '''
        create_clusters_table_query = '''CREATE TABLE IF NOT EXISTS clusters (
                                    cluster_id TEXT PRIMARY KEY,
                                    name TEXT NOT NULL,
                                    ip_address TEXT NOT NULL,
                                    port INTEGER NOT NULL);
                                    '''

        cursor = conn.cursor()
        print("Successfully Connected to SQLite")
        cursor.execute(create_cluster_info_table_query)
        cursor.execute(create_clusters_table_query)
        conn.commit()
        print("SQLite cluster table created")
        # create network table
        sqlite_create_network_table_query = '''CREATE TABLE IF NOT EXISTS network (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    cluster_id TEXT NOT NULL,
                                    throughput REAL NOT NULL,
                                    latency REAL NOT NULL,
                                    jitter REAL NOT NULL,
                                    date datetime);'''

        cursor = conn.cursor()
        print("Successfully Connected to SQLite")
        cursor.execute(sqlite_create_network_table_query)
        conn.commit()
        print("SQLite network table created")

        # create availability table
        sqlite_create_availability_table_query = '''CREATE TABLE IF NOT EXISTS availability (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    cluster_id TEXT NOT NULL,
                                    availability_score REAL NOT NULL,
                                    date datetime);'''

        cursor = conn.cursor()
        print("Successfully Connected to SQLite")
        cursor.execute(sqlite_create_availability_table_query)
        conn.commit()
        print("SQLite availability table created")

         # create terms table
        sqlite_create_terms_table_query = '''CREATE TABLE IF NOT EXISTS terms (
                                    cluster_url TEXT PRIMARY KEY,
                                    current_term TEXT NOT NULL);
                                    '''

        cursor = conn.cursor()
        print("Successfully Connected to SQLite")
        cursor.execute(sqlite_create_terms_table_query)
        conn.commit()
        print("SQLite terms table created")

        cursor.close()

    except sqlite3.Error as error:
        print("Error while creating a sqlite table", error)
    finally:
        # if conn:
        #     conn.close()
        print("sqlite connection is not closed")

def main():
    database = "metrics.db"

    # create a database connection
    conn = create_connection(database)
    with conn:
        print("first create table")
        create_table(conn)

    cluster_info = check_cluster_info()
    print(cluster_info)

    #initiate term on start
    current_url =  os.getenv('HOST_IP')
    term_record = initiate_terms_table(current_url)
    print(term_record)

#add rpc method for profile return verdict
@method
def peer_message_response(url,term) -> Result:
    print('from:', url)
    current_url =  os.getenv('HOST_IP')
    term_record = get_terms()
    if term_record is None:
       return Success({"data":{
           "message":"failed to fetch current term"
       }, "recieving_server": current_url, "requester_url": url, "code":"005", "reponse": False })
    
    local_term = int(term_record['current_term'])
    if local_term >= term:
        return Success({"data":{
           "message":"Higher term exists on the peer network",
           "term": local_term
        }, "recieving_server": current_url, "requester_url": url, "code":"004", "reponse": False })
    
    updated_record = update_term(current_url,str(term))
    if updated_record == "update failed":
           return Success({"data":{
           "message":"failed to update current term"
       }, "recieving_server": current_url, "requester_url": url, "code":"003", "reponse": False })
    
    elif updated_record is None:
          return Success({"data":{
           "message":"Updated current term but failed to fetch record"
       }, "recieving_server": current_url, "requester_url": url, "code":"002", "reponse": True })
    else:
        return Success({"data":{"updated_record":updated_record,
                                 "message":"Success"
                                },
                         "recieving_server": current_url, "requester_url": url, "code":"001", "reponse": True})


port = int(os.getenv('PORT', 5100))
host = os.getenv('HOST', 'localhost')
print('Port: ', port)
print('host: ', host)
if __name__ == "__main__":
    main()
    serve(host, port)
