from tcp_latency import measure_latency
from collections import Counter

cluster_list = [{"id":1, "cluster_name":"cr-dar", "ip": "196.32.212.213"}, {"id":2, "cluster_name":"cr-lsk", "ip": "196.32.215.213"}]
## may have a few repeated methods

def jitterCalculator(latencies):
    # Calculating difference list
    diff_list = []
    for x, y in zip(latencies[0::], latencies[1::]):
        diff_list.append(abs(y-x))
    sum = 0
    for i in diff_list:
        sum = sum + i
    return (sum/len(diff_list))

def modal_latency(values):
    values_counts = Counter(values)
    most_common = values_counts.most_common()
    modal_latency = most_common[0][0]
   # print(modal_latency)
    return modal_latency

def cluster_list_Latency(list):
    results_array=[]
    for item in list:
        latency_result = measure_latency(host=item['ip'], port=6443, runs=10, timeout=2.5)
        jitter_result = jitterCalculator(latency_result)
        modal_result = modal_latency(latency_result)
        results_array.append({'name':item['cluster_name'],'modal_latency':modal_result,'jitter':jitter_result})
    return results_array

def getClusterLatenciesAndJitter():
    resultObject = cluster_list_Latency(cluster_list)
    print(resultObject)
    return resultObject

# better comparison needed for all network metrics
def selectLeader():
    cluster_network_results = getClusterLatenciesAndJitter()
    # set chosen to first
    chosen_candidate = cluster_network_results[0]
    for cluster in cluster_network_results:
        if cluster['modal_latency'] < chosen_candidate['modal_latency']:
            chosen_candidate = cluster
    
    return chosen_candidate;

chosenLeader = selectLeader();
print(chosenLeader)