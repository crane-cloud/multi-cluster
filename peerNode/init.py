import socket
import random
import string
import os
import requests
import sqlite3
from util import create_db_connection, create_peer_tables, save_cluster_info
from jsonrpcserver import Success, method, serve,  InvalidParams, Result, Error

# Create the local cluster information (May need to be changed to support persistence)
def create_cluster_info():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    port = int(os.getenv('PORT'))
    name = "peer_" + hostname
    cluster_id = ip_address + ":" + str(port)

    cluster_info = {"cluster_id": cluster_id,
                    "name": name,
                    "ip_address": ip_address,
                    "port": port}
   
    print(cluster_info)

    return cluster_info

# Push the cluster information to the viewServer
def publish_cluster_info(cluster_info):
    url = f"{os.getenv('VIEWSERVER')}/clusters"

    print(url)

    if cluster_info:
        try:
            create = requests.post(url, json=cluster_info)

            if create.status_code == 201:
                print("New peer cluster information added to the ViewServer")

            elif create.status_code == 409:
                print("The peer cluster is already on the ViewServer")

            else:
                print(create.text)
                print("Unable to add the new peer cluster to the ViewServer")
                return None

        except Exception as e:
            print("Error: ", e)
            return None
    else:
        print ("No cluster information provided and/or created")
        return None


def main():
    
    cluster_info = create_cluster_info()

    # create a database connection
    conn = create_db_connection("peer.db")
    with conn:
        print("Creating the peer tables (init and cluster)")
        create_peer_tables(conn)

        if cluster_info:

            save_cluster_info(conn, cluster_info)

            publish_cluster_info(cluster_info)
    
    print(cluster_info)



#hostname = socket.gethostname()
#ip_address = socket.gethostbyname(hostname)
#port = int(os.getenv('PORT'))

#if __name__ == "__main__":
#    main()
    #serve(ip_address, port)
