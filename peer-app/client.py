from jsonrpclib import Server
import sys
from datetime import datetime
from latency import get_jitter, get_latency
from throughput import get_throughtput
import os

cluster_list = [{"id": 1, "cluster_name": "cis-lib1", "ip": "http://localhost:5141"},
                {"id": 2, "cluster_name": "dicts-01", "ip": "http://localhost:5142"}]


def main():
    port = 5141
    # port = os.getenv('PORT', 5141)
    server = Server(f'http://localhost:{port}')

    try:
        # INSERT NETWORK METRICS
        cluster_id = 1
        latency = get_latency()
        jitter = get_jitter()
        date = '25-11-2022'
        throughput = get_throughtput()
        metrics = (cluster_id, throughput, latency, jitter, date)
        print("Inserting network data: latency, throughput & jitter..")
        print(server.insert_network(metrics))

        # INSERT AVAILABILITY METRICS
        cluster_id = 1
        availability_score = 0
        date = '28-10-2022'
        print("Insert availability data..")
        metrics = (cluster_id, availability_score, date)
        print(server.insert_availability(metrics))

        # RETRIEVE all network METRICS
        print("GET network data..")
        print(server.select_all_network_metrics())

        # RETRIEVE METRICS per cluster
        cluster_id = 1
        metric_type = "network"
        print("Retrieve  " + metric_type +
              " data for cluster " + str(cluster_id))
        print(server.select_metrics_by_cluster(cluster_id, metric_type))

    except:
        print("Error: ", sys.exc_info())


if __name__ == '__main__':
    main()
