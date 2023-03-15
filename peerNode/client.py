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
from urlparse import urljoin

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
            print("Successfully pushed to Graphite")
        except Exception as e:
            print (e)
        sock.close()
    except Exception as me:
        #logging.error("Unable to push metrics to graphite")
        print(me)

#def pull_from_graphite(metrics):
    #http://ms0829.utah.cloudlab.us/render?target=128.110.217.54:5001.Network.L&format=json

    #clusters = retrieve_clusters_info()
    #for cluster in clusters:
    #    print("Each cluster metrics")

    #    url = urljoin(CARBON_SERVER, '/render')
    #    response = self.get(url, params={
    #        'target': metrics,
    #        'format': 'json',
    #        'from': '-%ss' % query_from,
    #    })
    #    data = response.json()
    #    A = requests.get(CARBON_SERVER)

#def compute_profile():
    print("Please compute the profile")

#def requestVote():
    #print("A request to be voted")

#def responseVote():
    #print("I voted for you")

def main():

    #while True:

        clusters = retrieve_clusters_info()
        
        for cluster in clusters:
            
            availability = check_availability(cluster["ip_address"], cluster["port"])

            if availability == 1:

                resources = check_cluster_resources(cluster["ip_address"], cluster["port"])
                network = check_network_resources(cluster["ip_address"], IPERF)

                if resources:
                    resource_message = [
                        '%s.%s.%s %f %d' % (cluster["cluster_id"].replace('.','_'), "Resource", "P", resources["cpu"], int(time.time())),
                        '%s.%s.%s %f %d' % (cluster["cluster_id"].replace('.','_'), "Resource", "M", resources["memory"], int(time.time())),
                        '%s.%s.%s %f %d' % (cluster["cluster_id"].replace('.','_'), "Resource", "D", resources["disk"], int(time.time()))
                        ]
                    graphite_r_message = '\n'.join(resource_message) + '\n'    
                    push_to_graphite(graphite_r_message)

                if network:
                    network_message = [
                        '%s.%s.%s %f %d' % (cluster["cluster_id"].replace('.','_'), "Network", "T", network["throughput"], int(time.time())),
                        '%s.%s.%s %f %d' % (cluster["cluster_id"].replace('.','_'), "Network", "L", network["latency"], int(time.time())),
                        '%s.%s.%s %f %d' % (cluster["cluster_id"].replace('.','_'), "Network", "J", network["jitter"], int(time.time()))
                        ]
                    graphite_n_message = '\n'.join(network_message) + '\n'    
                    push_to_graphite(graphite_n_message)

            availability_metric = '%s.%s.%s %d %d\n' % (cluster["cluster_id"].replace('.','_'), "Availability", "A", availability, int(time.time()))
            push_to_graphite(availability_metric)
        
        #time.sleep(DELAY)

if __name__ == '__main__':
    init.main()
    time.sleep(60)
    main()