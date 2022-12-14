import random
import string
import os
import requests
import sqlite3
from sqlite3 import Error


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn


def generate_cluster_info():
    cluster_info = {"cluster_id": str(random.randint(000000000, 9999999999)),
                    "name": f"clt-{os.getenv('CLUSTER_NAME', get_random_string(4))}",
                    "ip_address": "127.0.0.1",
                    "port": os.getenv('PORT', 5141)}
    return cluster_info


def get_cluster_info():
    database = "metrics.db"
    # create a database connection
    conn = create_connection(database)
    """
    Query tasks by priority
    :param conn: the Connection object
    :param priority:
    :return:
    """
    query = conn.execute(
        "SELECT * FROM cluster_info")
    conn.commit()

    if query:
        cluster = query.fetchone()
        cluster_info = {"cluster_id": cluster[0],
                        "name": cluster[1],
                        "ip_address": cluster[2],
                        "port": cluster[3]}
        return cluster_info
    else:
        return None


def save_cluster_info(cluster_info):
    database = "metrics.db"
    # create a database connection
    conn = create_connection(database)
    """
    Query tasks by priority
    :param conn: the Connection object
    :param priority:
    :return:
    """

    data_tuple = (cluster_info["cluster_id"],
                  cluster_info["name"],
                  cluster_info["ip_address"],
                  cluster_info["port"])

    query = conn.execute(
        "INSERT INTO cluster_info (cluster_id, name, ip_address, port) VALUES (?,?,?,?);", data_tuple)
    conn.commit()

    if not query:
        return None
    cluster = query.fetchone()
    cluster_info = {"cluster_id": cluster[0],
                    "name": cluster[1],
                    "ip_address": cluster[2],
                    "port": cluster[3]}
    return cluster_info


def check_cluster_info():
    url = f"{os.getenv('CENTRAL_SERVER_LINK')}/clusters"
    cluster_info = get_cluster_info()
    if cluster_info:
        return cluster_info

    payload = generate_cluster_info()

    try:
        respose = requests.post(url, json=payload)
        if respose.status_code == 409:
            print("Cluster already exists")
            print(respose.data)
            return False
        elif respose.status_code == 201:
            print("Successfully joined network")
            return save_cluster_info(payload)
        else:
            print(respose.text)
            print("Error joining network")
            return None
    except Exception as e:
        print("Error: ", e)
        return None
