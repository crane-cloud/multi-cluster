import sqlite3
from sqlite3 import Error
import requests
import os
from jsonrpcserver import Success, method, serve,  InvalidParams, Result, Error
import psutil
from tcp_latency import measure_latency
import iperf3


def create_db_connection(db):
    """ create a database connection to the SQLite database
        specified by the db
    :param db: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db)
    except Error as e:
        print(e)

    return conn


def create_peer_tables(conn):
    try:
        # Cluster information table
        create_cluster_info_table_query = '''CREATE TABLE IF NOT EXISTS init (
                                    cluster_id TEXT PRIMARY KEY,
                                    name TEXT NOT NULL,
                                    ip_address TEXT NOT NULL,
                                    port INTEGER NOT NULL);
                                    '''
        create_clusters_table_query = '''CREATE TABLE IF NOT EXISTS cluster (
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
        
        print("SQLite cluster information table created")

        cursor.close()

    except sqlite3.Error as error:
        print("Error while creating the sqlite peer table(s)", error)

    finally:
        # if conn:
        #     conn.close()
        print("sqlite connection is not closed")

def save_cluster_info(conn, cluster_info):

    data_tuple = (cluster_info["cluster_id"],
                  cluster_info["name"],
                  cluster_info["ip_address"],
                  cluster_info["port"])

    conn.execute(
        "INSERT OR IGNORE INTO init (cluster_id, name, ip_address, port) VALUES (?,?,?,?);", data_tuple)
    conn.commit()

def save_clusters_info(conn, cluster_info):

    data_tuple = (cluster_info["cluster_id"],
                  cluster_info["name"],
                  cluster_info["ip_address"],
                  cluster_info["port"])

    conn.execute(
        "INSERT OR IGNORE INTO cluster (cluster_id, name, ip_address, port) VALUES (?,?,?,?);", data_tuple)
    conn.commit()

def retrieve_clusters_info ():
    print("Retrieve all the clusters from the ViewServer")
    url = f"{os.getenv('VIEWSERVER')}/clusters"

    try:
        request = requests.get(url)
            
        if request.status_code == 200:
            print("Clusters retrieval success")
            clusters = request.json().get("clusters")
            return clusters
        else:
            print("Failed to retrieve the clusters")
            return None
    except Exception as e:
        print("Error: ", e)
        return None


def check_availability(host, port):
    try:
        serv_conn = Server("http://"+host+":"+str(port))
        if serv_conn:
            resp = serv_conn.get_availability()
        print(resp)
        if resp["status"] == 200:
            return 1
    except:
        return 0


# Pick CPU, Memory and Disk metrics 
def getCPU():
    percent_cpu = psutil.cpu_percent()
    print(percent_cpu)
    return percent_cpu


def getMemory():
    percent_memory = psutil.virtual_memory().percent
    return percent_memory


def getDisk():
    tot_disk = psutil.disk_usage(os.sep)
    percent_disk = psutil.disk_usage(os.sep).percent
    return tot_disk



def check_cluster_resources(host, port):
    try:
        serv_conn = Server("http://"+host+":"+str(port))
        if serv_conn:
            resp = serv_conn.get_cluster_resources()
        if resp["status"] == 200:
            print(resp)
            return resp["data"]

        else:
            return None
    except:
        return None


def check_network_resources(host, port):
    return None
