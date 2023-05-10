import requests
from  profile_controller.get_metrics import get_availability, generic_get_direct_percentile_value  
from profile_controller.network_compute_helpers import get_average
from profile_controller.compute_weights import handle_metrics_list
import threading

# from profiles_cache import 

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
    # latency95percentile =  get_percentiles(generic_get_metrics(ip,'Network.L'),95)
    # jitter95percentile =  get_percentiles(generic_get_metrics(ip, 'Network.J'),95)
    # throughput95percentile =  get_percentiles(generic_get_metrics(ip, 'Network.T'),95)
    # cpu95percentile =  get_percentiles(generic_get_metrics(ip, 'Resource.P'),95)
    # memory95percentile =  get_percentiles(generic_get_metrics(ip, 'Resource.M'),95)
    # disk95percentile =  get_percentiles(generic_get_metrics(ip, 'Resource.D'),95)
    latency95percentile =  generic_get_direct_percentile_value(ip,'Network.L')
    jitter95percentile =  generic_get_direct_percentile_value(ip, 'Network.J')  
    throughput95percentile =  generic_get_direct_percentile_value(ip, 'Network.T')
    cpu95percentile =  generic_get_direct_percentile_value(ip, 'Resource.P')
    memory95percentile =  generic_get_direct_percentile_value(ip, 'Resource.M')
    disk95percentile =  generic_get_direct_percentile_value(ip, 'Resource.D')
    availabilityAverage=  get_average(get_availability(ip))

    return {"latency":latency95percentile,"jitter":jitter95percentile,"throughput":throughput95percentile,
           "cpu":cpu95percentile,"memory":memory95percentile,"disk":disk95percentile, "availability":availabilityAverage, "ip":ip}

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
    # print("---Collected Metrics--")
    # print(cluster_metrics)
    weighted_metrics = handle_metrics_list(cluster_metrics)
    return weighted_metrics


# if __name__ == "__main__":
#     # get cluster ips
#     cluster_ips =  get_cluster(clusters_url)
#     # get metrics for different clusters
#     cluster_metrics = []
#     threads = []
#     for ip in cluster_ips:
#         t = threading.Thread(target=lambda: cluster_metrics.append(get_metrics(ip)))
#         t.start()
#         threads.append(t)
        
#     for t in threads:
#         t.join()
#     # print("---Collected Metrics--")
#     # print(cluster_metrics)
#     weighted_metrics = handle_metrics_list(cluster_metrics)
#     # print("---weighted profiles---")
#     # print(weighted_metrics)



    
    