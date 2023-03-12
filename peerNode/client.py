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

hostname = socket.gethostname()
CARBON_SERVER = socket.gethostbyname(hostname)
CARBON_PORT = int(os.getenv('CARBON_PORT'))
DELAY = int(os.getenv("DELAY"))
IPERF = int(os.getenv("IPERF"))


def push_to_graphite(metrics):
    #logging.info("Pushing metrics to the Graphite Server")
    print ("Pushing metrics to the Graphite Server")
    #logging.info(metrics)
    print(metrics)
    try:
        sock = socket.socket()
        sock.connect((CARBON_SERVER, CARBON_PORT))
        try:
            sock.sendall(str.encode(metrics))
        except Exception as e:
            print (e)
        sock.close()
    except Exception as me:
        #logging.error("Unable to push metrics to graphite")
        print(me)

def main():

    while True:

        clusters = retrieve_clusters_info()
        
        for cluster in clusters:
            
            availability = check_availability(cluster["ip_address"], cluster["port"])

            if availability == 1:

                resources = check_cluster_resources(cluster["ip_address"], cluster["port"])
                network = check_network_resources(cluster["ip_address"], IPERF)

                if resources:
                    resource_message = [
                        '%s %s %s %f %d' % (cluster["cluster_id"], "Resource", "P", resources["cpu"], int(time.time())),
                        '%s %s %s %f %d' % (cluster["cluster_id"], "Resource", "M", resources["memory"], int(time.time())),
                        '%s %s %s %f %d' % (cluster["cluster_id"], "Resource", "D", resources["disk"], int(time.time()))
                        ]
                    graphite_r_message = '\n'.join(resource_message) + '\n'    
                    push_to_graphite(graphite_r_message)

                if network:
                    network_message = [
                        '%s %s %s %f %d' % (cluster["cluster_id"], "Network", "T", network["throughput"], int(time.time())),
                        '%s %s %s %f %d' % (cluster["cluster_id"], "Network", "L", network["latency"], int(time.time())),
                        '%s %s %s %f %d' % (cluster["cluster_id"], "Network", "J", network["jitter"], int(time.time()))
                        ]
                    graphite_n_message = '\n'.join(network_message) + '\n'    
                    push_to_graphite(graphite_n_message)

            availability_metric = '%s %s %s %d %d\n' % (cluster["cluster_id"], "Availability", "A", availability, int(time.time()))
            push_to_graphite(availability_metric)
        
        time.sleep(DELAY)

if __name__ == '__main__':
    main()