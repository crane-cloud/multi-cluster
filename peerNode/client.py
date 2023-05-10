from jsonrpclib import Server
import sys
from datetime import datetime
from util import retrieve_clusters_info, check_availability, check_cluster_resources
from network import check_network_resources
import requests
import os
import socket
import time
import logging
import init
#from urlparse import urljoin

#cache requirements
import functools
import json
from collections import deque
import threading

from profile_controller.controller import profile_controller

hostname = socket.gethostname()
CARBON_SERVER = socket.gethostbyname(hostname)
CARBON_PORT = int(os.getenv('CARBON_PORT'))
DELAY = int(os.getenv("DELAY"))
IPERF = int(os.getenv("IPERF"))

cached_data_queue = deque(maxlen=10)

def push_to_graphite(metrics):
    #logging.info("Pushing metrics to the Graphite Server")
    print ("Pushing metrics to the Graphite Server")
    #logging.info(metrics)
    print(metrics)
    try:
        sock = socket.socket()
        sock.connect((CARBON_SERVER, CARBON_PORT))
        sock.settimeout(5)
        try:
            sock.sendall(str.encode(metrics))
            print("Successfully pushed to Graphite")
        except Exception as e:
            print (e)
            return
        sock.close()
    except Exception as me:
        #logging.error("Unable to push metrics to graphite")
        print(me)
        return

def retrieve_save_peer_resources(cluster):
    try:
        resources = check_cluster_resources(cluster["ip_address"], cluster["port"])
        if resources:
            resource_message = [
                '%s.%s.%s %f %d' % (cluster["cluster_id"].replace('.','_').replace(':','_'), "Resource", "P", resources["cpu"], int(time.time())),
                '%s.%s.%s %f %d' % (cluster["cluster_id"].replace('.','_').replace(':','_'), "Resource", "M", resources["memory"], int(time.time())),
                '%s.%s.%s %f %d' % (cluster["cluster_id"].replace('.','_').replace(':','_'), "Resource", "D", resources["disk"], int(time.time()))
            ]
            graphite_r_message = '\n'.join(resource_message) + '\n'    
            push_to_graphite(graphite_r_message)
        else:
            return None
    except Exception as e:
        print(e)

def retrieve_save_network_resources(cluster, port):
    try:
        network = check_network_resources(cluster["ip_address"], port)
        if network:
            network_message = [
                '%s.%s.%s %f %d' % (cluster["cluster_id"].replace('.','_').replace(':','_'), "Network", "T", network["throughput"], int(time.time())),
                '%s.%s.%s %f %d' % (cluster["cluster_id"].replace('.','_').replace(':','_'), "Network", "L", network["latency"], int(time.time())),
                '%s.%s.%s %f %d' % (cluster["cluster_id"].replace('.','_').replace(':','_'), "Network", "J", network["jitter"], int(time.time()))
                ]
            graphite_n_message = '\n'.join(network_message) + '\n'    
            push_to_graphite(graphite_n_message)
        else:
            return None
    except Exception as e:
        print(e)

@functools.lru_cache(maxsize=None)
def cached_data():
    print("Retriving new data points:")
    data = profile_controller()
    cached_data_queue.append(json.dumps(data))
    return cached_data_queue[-1] 

def get_cached_data():
    if not cached_data_queue:
        return []
    return json.loads(cached_data_queue[-1])

def run_cached_data():
    while True:
        print(cached_data())
        time.sleep(10)
    

def main():

    while True:
        # Fetch all the clusters from the view
        clusters = retrieve_clusters_info()
        
        # For each cluster, retrieve, measure and push to the graphite tsdb
        for cluster in clusters:
            
            # We first check for the availability of the cluster
            availability = check_availability(cluster["ip_address"], cluster["port"])

            # If the cluster is available, we can go ahead and measure/retrieve the values
            if availability == 1:
                retrieve_save_peer_resources(cluster)
                retrieve_save_network_resources(cluster, IPERF)

            # Regardless of the peer availability, the A metric should have a value
            availability_metric = '%s.%s.%s %d %d\n' % (cluster["cluster_id"].replace('.','_').replace(':','_'), "Availability", "A", availability, int(time.time()))
            push_to_graphite(availability_metric)
        
        # We set the loop sleep time to 10 minutes
        time.sleep(600)

if __name__ == '__main__':
    init.main()
    # Start a new thread to run the cached_data() function periodically
    # t = threading.Thread(target=run_cached_data)
    # t.daemon = True
    # t.start()

    # Allow fpr the nodes to register at the view
    time.sleep(60)
    
    main()