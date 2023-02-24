from jsonrpclib import Server
import sys
from datetime import datetime
from metrics import get_jitter, get_latency
from discovery import get_cluster_info, save_cluster_info, generate_cluster_info
import requests
from metrics import get_throughtput
import os



def main():
    port = 5100
    # port = os.getenv('PORT', 5141)
    server = Server(f'http://localhost:{port}')


    try:
        # PERFORM CLUSTER DISCOVERY THEN INSERT NETWORK & AVAILABILITY METRICS FOR ALL CLUSTERS        
        # clusters_list = get_cluster_info() # fetch and print cluster list 
        # print(clusters_list)
        # loop through cluster list while getting metrics on latency and jitter then store them
        # for cluster in clusters_list["clusters_list"]:
        #     print(cluster[2])
        #     print(cluster[3])
        #     store_metrics(server,cluster[2], cluster[3], cluster[0])

        # Get server metrics
        print("Get server metrics")
        print(server.get_server_resources())

        # RETRIEVE all network METRICS 
        # print("GET network data..")
        # print(server.select_all_network_metrics())

        # RETRIEVE METRICS per cluster
        # cluster_id = 1
        # metric_type = "network"
        # print("Retrieve  " + metric_type +
        #       " data for cluster " + str(cluster_id))
        # print(server.select_metrics_by_cluster(cluster_id, metric_type))


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

def check_availability(host,port):
    try:
        serv_conn = Server("http://"+host+":"+str(port))
        if serv_conn:
            resp = serv_conn.check_availability()
        # r =requests.post("http://"+host+":"+str(port))
        print(resp)
        if resp["status"] == 200:
            return 1
    except:
        return 0


if __name__ == '__main__':
    main()
