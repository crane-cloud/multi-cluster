import random
import string
import os
import requests
import sqlite3


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
                    "name": os.getenv('CLUSTER_NAME', f"clt-{get_random_string(4)}"),
                    "ip_address": os.getenv('HOST_IP', "127.0.0.2"), 
                    "chosen_cluster": "",
                    "port": os.getenv('PORT', 5141)}
    return cluster_info


def check_cluster_info():
    print('Getting cluster info')
    url = f"{os.getenv('CENTRAL_SERVER_LINK')}/clusters"
    cluster_info = get_cluster_info()

    if cluster_info:
        return cluster_info

    payload = generate_cluster_info()

    try:
        respose = requests.post(url, json=payload)

        if respose.status_code == 201:
            print("Successfully joined network")
            return save_cluster_info(payload)
        elif respose.status_code == 409:
            print("Error: Cluster already exists")
            print(respose.text)
            return None
        else:
            print(respose.text)
            print("Error joining network")
            return None
    except Exception as e:
        print("Error: ", e)
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
                  cluster_info["chosen_cluster"],
                  cluster_info["port"])

    conn.execute(
        "INSERT INTO cluster_info (cluster_id, name, ip_address, chosen_cluster, port) VALUES (?,?,?,?,?);", data_tuple)
    conn.commit()

    return get_cluster_info()


def get_cluster_info():
    database = "metrics.db"
    # create a database connection
    conn = create_connection(database)
    try:
        query = conn.execute(
            "SELECT * FROM cluster_info")
        conn.commit()
        cluster = query.fetchone()
        if cluster:
            # Fetch and update clusters list
            clusters = update_clusters_list(cluster[0])
            cluster_info = {"cluster_id": cluster[0],
                            "name": cluster[1],
                            "ip_address": cluster[2],
                            "chosen_cluster": cluster[3],
                            "port": cluster[4]}
            return {'current_cluster': cluster_info, 'clusters_list': clusters}
        else:
            return None
    except Exception as e:
        print("Error: ", e)
        return None    


def update_clusters_list(current_cluster_id):
    # get all clusters from the central server
    url = f"{os.getenv('CENTRAL_SERVER_LINK')}/clusters"
    try:
        respose = requests.get(url)
        if respose.status_code == 200:
            print("Successfully picked clusters")
            clusters = respose.json().get("clusters")
        else:
            print("Error getting clusters from central server")
            print(respose.text)
            return None
    except Exception as e:
        print("Error: ", e)
        return None

    database = "metrics.db"
    # create a database connection
    print("Updating clusters")
    conn = create_connection(database)
    # add clusters to the database
    for cluster in clusters:
        if str(cluster['cluster_id']) == str(current_cluster_id):
            continue
        data_tuple = (cluster["cluster_id"],
                      cluster["name"],
                      cluster["ip_address"],
                      cluster["chosen_cluster"],
                      cluster["port"])
        try:
            conn.execute(
                "INSERT INTO clusters (cluster_id, name, ip_address, chosen_cluster, port) VALUES (?,?,?,?,?);", data_tuple)
            conn.commit()
        except sqlite3.IntegrityError as e:
            # Update info of the cluster if it already exists
            conn.execute(
                "UPDATE clusters SET name = ?, ip_address = ?, chosen_cluster = ?, port = ? WHERE cluster_id = ?;", (cluster["name"], cluster["ip_address"], cluster["port"], cluster["chosen_cluster"], cluster["cluster_id"]))
        except Exception as e:
            print(f'Error: {e}')
            return None

    get_clusters_query = conn.execute("SELECT * FROM clusters")
    conn.commit()
    clusters = get_clusters_query.fetchall()
    return clusters

def update_leader_on_cluster(cluster_id,chosen_cluster):
    database = "metrics.db"
    # create a database connection
    print("Updating cluster leader")
    conn = create_connection(database)
    try:
        conn.execute("UPDATE cluster_info SET chosen_cluster = ? WHERE cluster_id = ?", (chosen_cluster,cluster_id))
        conn.commit()
        print('cluster leader updated')
        return True
    except Exception as e:
        print(f'Error: {e}')
        return None
    

def update_server_leader(cluster_id,leader_id):
    url = f"{os.getenv('CENTRAL_SERVER_LINK')}/clusters/{cluster_id}"
    try:
        respose = requests.patch(url,json={"chosen_cluster": leader_id,})
        if respose.status_code == 200:
            print("Successfully update clusters")
        else:
            print("Error updating central server cluster information")
            print(respose.text)
            return None
    except Exception as e:
        print("Error: ", e)
        return None