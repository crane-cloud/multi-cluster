import requests
from get_metrics import get_network_latency, get_cpu, get_disk, get_memory,get_network_jitter,get_network_throughput 
from network_compute_helpers import get_percentiles
from compute_weights import handle_metrics_list
import threading

clusters_url = 'http://view.cranecloud.africa:5000/clusters'

def get_cluster(url):
    # emulate source of the metrics
    response = requests.get(clusters_url)
    cluster_ips =[]
    if response.status_code == 200:
        data = response.json()
        clusters = data['clusters']
        for cluster in clusters:
            cluster_ips.append(cluster['cluster_id'])    
        print(cluster_ips)
        return cluster_ips;   
    else:
        print(f'Request failed with status code {response.status_code}')
        return None

def get_metrics(ip):
    latency95percentile =  get_percentiles(get_network_latency(ip),95)
    jitter95percentile =  get_percentiles(get_network_jitter(ip),95)
    throughput95percentile =  get_percentiles(get_network_throughput(ip),95)
    cpu95percentile =  get_percentiles(get_cpu(ip),95)
    memory95percentile =  get_percentiles(get_memory(ip),95)
    disk95percentile =  get_percentiles(get_disk(ip),95)
    return {"latency":latency95percentile,"jitter":jitter95percentile,"throughput":throughput95percentile,
           "cpu":cpu95percentile,"memory":memory95percentile,"disk":disk95percentile, "ip":ip}

if __name__ == "__main__":
    # get cluster ips
    cluster_ips =  get_cluster(clusters_url)
    # get metrics for different clusters
    cluster_metrics = []
    threads = []
    for ip in cluster_ips:
        t = threading.Thread(target=lambda: cluster_metrics.append(get_metrics(ip)))
        t.start()
        threads.append(t)
        
    for t in threads:
        t.join()
    print("---Collected Metrics--")
    print(cluster_metrics)
    weighted_metrics = handle_metrics_list(cluster_metrics)
    print("---weighted profiles---")
    print(weighted_metrics)


    
    