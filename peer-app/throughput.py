import iperf3
#import json
client = iperf3.Client()
#client.duration = 1
#lsk
client.server_hostname = '196.32.215.213'
client.port = 31995
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
    

def get_throughtput():
    return (result.sent_Mbps+ result.received_Mbps)/2 