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

def get_latency(host,port):
    latency_result = measure_latency(host=host, port=port, runs=10, timeout=2.5)
    print("Latency Test results:")
    print(latency_result)
    return latency_result
#faster testing
def get_jitter(latency_result):
    jitter_result = jitterCalculator(latency_result)
    print(jitter_result)
    return round(jitter_result,3)