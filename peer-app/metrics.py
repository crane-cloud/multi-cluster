import os
import psutil
from tcp_latency import measure_latency
import iperf3



# Pick CPU, Memory and Disk metrics 
def getCPU():
    percent_cpu = psutil.cpu_percent()
    print(percent_cpu)
    return percent_cpu


def getMemory():
    percent_memory = psutil.virtual_memory().percent
    return percent_memory


def getDisk():
    tot_disk = psutil.disk_usage(os.sep)
    percent_disk = psutil.disk_usage(os.sep).percent
    return tot_disk


# Pick latency and gitter values

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
    return round(latency_result[0],3)

def get_jitter(host,port):
    latency_result = measure_latency(host=host, port=port, runs=10, timeout=2.5)
    print("Latency Test results:")
    print(latency_result)
    print('')
    print('Jitter from latency values, (ms)')
    jitter_result = jitterCalculator(latency_result)
    print(jitter_result)
    return round(jitter_result,3)



# Pick throughput metrics
client = iperf3.Client()

def get_throughtput(host):
    client.server_hostname = host
    client.port = 5201
    client.protocol = 'tcp'


    print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))
    result = client.run()
    #result is a class Testresult
    if result.error:
        print(result.error)
    else:
        #print(result)
        print('')
        print('Throughput Test completed:')
        #udp protocol results
        #print('  started at         {0}'.format(result.time))
        #print('  bytes transmitted  {0}'.format(result.bytes))
        #print('  jitter (ms)        {0}'.format(result.jitter_ms))
        #print('  avg cpu load       {0}%\n'.format(result.local_cpu_total))

        print('Average sum sent:')
        print('  bits per second      (bps)   {0}'.format(result.sent_bytes))
        print('  bytes sent      (bytes)   {0}'.format(result.sent_bps))
        print('  kilobits sent      (kbps)   {0}'.format(result.sent_kbps))
        print('  Megabits sent      (mbps)   {0}'.format(result.sent_Mbps))

        print('Average sum received:')
        print('  bits per second      (bps)   {0}'.format(result.received_bps))
        print('  bytes received      (bytes)   {0}'.format(result.received_bytes))
        print('  kilobits sent      (kbps)   {0}'.format(result.received_kbps))
        print('  Megabits sent      (mbps)   {0}'.format(result.received_Mbps))
        

    client.close()
    return (result.sent_Mbps+ result.received_Mbps)/2 