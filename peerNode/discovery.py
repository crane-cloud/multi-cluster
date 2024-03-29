import random
import string
import os
import requests
import sqlite3
from util import create_db_connection, save_clusters_info, retrieve_clusters_info

remote_clusters = retrieve_clusters_info()

def update_clusters_list():
    conn = create_db_connection("peer.db")

    with conn:
        print("Local creation or update of the cluster information")
        for cluster in remote_clusters:
            #data_tuple = (cluster["cluster_id"],
            #              cluster["name"],
            #              cluster["ip_address"],
            #              cluster["port"])
            
            try:
                print(cluster)
                save_clusters_info(conn, cluster)

            except Exception as e:
                print(f'Error: {e}')
                return None

update_clusters_list()