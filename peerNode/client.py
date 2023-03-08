from jsonrpclib import Server
import sys
from datetime import datetime
from metrics import get_jitter, get_latency
from discovery import get_cluster_info, save_cluster_info, generate_cluster_info
from util import retrieve_clusters_info, get_availability
import requests
from metrics import get_throughtput
import os
import socket
import time


CARBON_SERVER = os.getenv("CARBON_SERVER")
CARBON_PORT = os.getenv("CARBON_PORT")
DELAY = os.getenv("DELAY")

def main():

    while True:
        clusters = retrieve_clusters_info()
        
        timestamp = int(time.time())
    
    for cluster in clusters:
        
        availability = get_availability(cluster["ip_address"], cluster["port"])

        if availability == 1:
            resources = get_cluster_resources (cluster["ip_address"], cluster["port"])
            network = get_network_resources (cluster["ip_address"], cluster["port"])
        
        else:

            return None


    port = 5001
    server = Server(f'http://localhost:{port}')

    try:
        print("Get server metrics")
        print(server.get_server_resources())

    except:
        print("Error: ", sys.exc_info())







def store_metrics(server, host, port, cluster_id):
    latency = get_latency(host,port)
    jitter = get_jitter(host,port)
    date = datetime.date
    print("Get throughput.....")
    throughput = get_throughtput(host)
    print(throughput)
    metrics = (cluster_id, throughput,latency,jitter, str(date))
    print(metrics)
    print("Inserting network data: latency, throughput & jitter..")
    resp = server.insert_network(metrics)
    print(resp)

    # insert availability metrics
    print("Handle availability....")
    availability_score = check_availability(host,port)
    print(availability_score)
    metrics = (cluster_id, availability_score, str(date))
    print(metrics)
    print(server.insert_availability(metrics))



if __name__ == '__main__':
    main()
