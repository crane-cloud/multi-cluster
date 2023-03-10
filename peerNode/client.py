from jsonrpclib import Server
import sys
from datetime import datetime
#from metrics import get_jitter, get_latency
#from discovery import get_cluster_info, save_cluster_info, generate_cluster_info
from util import retrieve_clusters_info, check_availability, check_cluster_resources
import requests
#from metrics import get_throughtput
import os
import socket
import time

hostname = socket.gethostname()
CARBON_SERVER = socket.gethostbyname(hostname)
CARBON_PORT = int(os.getenv('CARBON_PORT'))
DELAY = int(os.getenv("DELAY"))


def push_to_graphite(metrics):
    print ("Pushing metrics to the Graphite Server")
    print(metrics)
    sock = socket.socket()
    sock.connect((CARBON_SERVER, CARBON_PORT))
    sock.sendall(metrics.encode())
    sock.close()


def main():

    while True:

        clusters = retrieve_clusters_info()
        
        for cluster in clusters:
            
            availability = check_availability(cluster["ip_address"], cluster["port"])

            if availability == 1:

                resources = check_cluster_resources(cluster["ip_address"], cluster["port"])

                if resources:
                    resource_message = [
                        '%s %s %s %d %d' % (cluster["cluster_id"], "Resource", "P", resources["cpu"], int(time.time())),
                        '%s %s %s %d %d' % (cluster["cluster_id"], "Resource", "M", resources["memory"], int(time.time())),
                        '%s %s %s %d %d' % (cluster["cluster_id"], "Resource", "D", resources["disk"], int(time.time()))
                        ]
                    graphite_r_message = '\n'.join(resource_message) + '\n'    
                    push_to_graphite(graphite_r_message)

            #lines = [
            #'%s %s %s %d %d' % (cluster["cluster_id"], "Availability", "A", availability, int(time.time()))
            #'system.%s.loadavg_5min %s %d' % (node, loadavgs[1], timestamp),
            #'system.%s.loadavg_15min %s %d' % (node, loadavgs[2], timestamp)
            #]

            #if availability == 1:
            #    resources = get_cluster_resources(cluster["ip_address"], cluster["port"])
            #    network = get_network_resources(cluster["ip_address"], cluster["port"])
        
            #else:

            #    return None
            availability_metric = '%s %s %s %d %d\n' % (cluster["cluster_id"], "Availability", "A", availability, int(time.time()))
            push_to_graphite(availability_metric)
        
        time.sleep(DELAY)


#    port = 5001
#    server = Server(f'http://localhost:{port}')

#    try:
#        print("Get server metrics")
#        print(server.get_server_resources())

#    except:
#        print("Error: ", sys.exc_info())

#def store_metrics(server, host, port, cluster_id):
#   latency = get_latency(host,port)
#    jitter = get_jitter(host,port)
#    date = datetime.date
#    print("Get throughput.....")
#    throughput = get_throughtput(host)
#    print(throughput)
#    metrics = (cluster_id, throughput,latency,jitter, str(date))
#    print(metrics)
#    print("Inserting network data: latency, throughput & jitter..")
#    resp = server.insert_network(metrics)
#    print(resp)

    # insert availability metrics
#    print("Handle availability....")
#    availability_score = check_availability(host,port)
#    print(availability_score)
#    metrics = (cluster_id, availability_score, str(date))
#    print(metrics)
#    print(server.insert_availability(metrics))

#if __name__ == '__main__':
#    main()
