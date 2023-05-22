import requests
from  profile_controller.get_metrics import get_availability, getp_value  
from profile_controller.network_compute_helpers import get_average
from profile_controller.compute_weights import handle_metrics_list
import threading
import socket

clusters_url = 'http://view.cranecloud.africa:5000/clusters'

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
cluster_id = ip_address + ":5001"

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
    lp95 =  getp_value(ip,'Network.L')
    jp95 =  getp_value(ip, 'Network.J')  
    tp95 =  getp_value(ip, 'Network.T')
    pp95 =  getp_value(ip, 'Resource.P')
    mp95 =  getp_value(ip, 'Resource.M')
    dp95 =  getp_value(ip, 'Resource.D')
    av =  get_average(get_availability(ip))

    return {"latency":lp95, "jitter":jp95, "throughput":tp95,
           "cpu":pp95,"memory":mp95,"disk":dp95, "availability":av, "ip":ip}

def profile_controller():
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
    weighted_metrics = handle_metrics_list(cluster_metrics)
    return weighted_metrics