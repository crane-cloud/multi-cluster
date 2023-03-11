import tcp_latency
from tcp_latency import measure_latency
import iperf3

client = iperf3.Client()

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
    latency_result = measure_latency(host=host, port=port, runs=10, timeout=2.5)
    print("Latency Test results:")
    print(latency_result)
    return round(latency_result[0],3)

def get_jitter(host, port):
    latency_result = measure_latency(host=host, port=port, runs=10, timeout=2.5)
    print("Latency Test results:")
    print(latency_result)
    print('')
    print('Jitter from latency values, (ms)')
    jitter_result = jitterCalculator(latency_result)
    print(jitter_result)
    return round(jitter_result,3)

def get_throughtput(host, port):
    client.server_hostname = host
    client.port = port
    client.protocol = 'tcp'

    print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))
    result = client.run()
    #result is a class Testresult
    
    if result.error:
        print(result.error)
        return None

    else:
        print('')
        print('Throughput Test completed:')

        print('Average sum sent:')
        print('Megabits sent      (mbps)   {0}'.format(result.sent_Mbps))

        print('Average sum received:')
        print('Megabits sent      (mbps)   {0}'.format(result.received_Mbps))
        
    #client.close()

    return (result.sent_Mbps+ result.received_Mbps)/2


def check_network_resources(host, port):
    throughput = get_throughtput(host, port)
    latency = get_latency(host, port)
    jitter = get_jitter(host, port)

    network_resources = {"throughput": throughput, "latency": latency, "jitter": jitter}
    
    print(network_resources)
    return network_resources

## Manual test
#def main():
#    check_network_resources("128.110.217.44", 5201)

#if __name__ == '__main__':
#    main()