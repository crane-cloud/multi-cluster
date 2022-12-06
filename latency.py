from tcp_latency import measure_latency
from collections import Counter


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

latency_result = measure_latency(host='196.32.212.213', port=6443, runs=10, timeout=2.5)
print("Latency Test results:")
print(latency_result)
print('')
print('modal latency')
print(modal_latency(latency_result))
print('Jitter from latency values, (ms)')
jitter_result = jitterCalculator(latency_result)
modal_result = modal_latency(latency_result)
print(jitter_result)

def get_latency():
    return latency_result[0]

def get_jitter():
    return jitter_result

def get_latency_modal():
    return modal_result

# class clusterLatencyAndJiter:
#     def __init__(self, name, latency_modal,jitter):
#         self.name = name
#         self.latency_modal = latency_modal
#         self.jitter = jitter

# def cluster_list_Latency(list):
#     results_array=[]
#     for item in list:
#         latency_result = measure_latency(host=item['ip'], port=6443, runs=10, timeout=2.5)
#         jitter_result = jitterCalculator(latency_result)
#         modal_result = modal_latency(latency_result)
#         results_array.append({'name':item['cluster_name'],'modal_latency':modal_result,'jitter':jitter_result})
#     return results_array

