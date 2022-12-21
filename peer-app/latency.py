from tcp_latency import measure_latency

def jitterCalculator(latencies):
    # Calculating difference list
    diff_list = []
    for x, y in zip(latencies[0::], latencies[1::]):
        diff_list.append(abs(y-x))
    sum = 0
    for i in diff_list:
        sum = sum + i
    return (sum/len(diff_list))


latency_result = measure_latency(host='196.32.212.213', port=6443, runs=10, timeout=2.5)
print("Latency Test results:")
print(latency_result)
print('')
print('Jitter from latency values, (ms)')
jitter_result = jitterCalculator(latency_result)
print(jitter_result)

def get_latency():
    return latency_result[0]

def get_jitter():
    return jitter_result