import tcp_latency
from tcp_latency import measure_latency
import iperf3

def jitterCalculator(latencies):
    # Calculating difference list
    diff_list = []
    for x, y in zip(latencies[0::], latencies[1::]):
        diff_list.append(abs(y-x))
    sum = 0
    for i in diff_list:
        sum = sum + i
    return (sum/len(diff_list))

def get_latency(host, port):
    latency_result = measure_latency(host=host, port=port, runs=4, timeout=2.0)
    #print("Latency Test results:")
    print(latency_result)

    avg_latency = sum(latency_result) / len(latency_result)

    return round(avg_latency, 3)

def get_jitter(host, port):
    latency_result = measure_latency(host=host, port=port, runs=4, timeout=2.0)
    #print("Latency Test results:")
    #print(latency_result)
    #print('')
    #print('Jitter from latency values, (ms)')
    jitter_result = jitterCalculator(latency_result)
    print(jitter_result)
    return round(jitter_result, 3)

def get_throughtput(host, port):
    
    try:
        client = iperf3.Client()
        client.server_hostname = host
        client.port = port
        client.protocol = 'tcp'
        client.zerocopy = True
        client.duration = int(3)
        
        print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))
        result = client.run()

    except Exception as e:
        print(e)
        return 0.0
    
    if result.error:
        print(result.error)
        return 0.0

    else:
        print('Megabits sent      (Mbps)   {0}'.format(result.sent_Mbps))
        print('Megabits sent      (Mbps)   {0}'.format(result.received_Mbps))
        
        #client.close()
        avg_throughput = (result.sent_Mbps+ result.received_Mbps)/2
        print(avg_throughput)
        return round(avg_throughput, 3)

def check_network_resources(host, port):
    throughput = get_throughtput(host, port)
    latency = get_latency(host, port)
    jitter = get_jitter(host, port)

    network_resources = {"throughput": throughput, "latency": latency, "jitter": jitter}
    
    print(network_resources)
    return network_resources