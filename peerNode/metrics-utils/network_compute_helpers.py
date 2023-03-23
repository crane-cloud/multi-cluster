import requests
import numpy as np
from scipy import stats

latency_url = 'http://cr-dar.cranecloud.africa/render?target=102_134_147_244_5001.Network.L&format=json'
jitter_url = 'http://cr-dar.cranecloud.africa/render?target=102_134_147_244_5001.Network.J&format=json'
throughput_url = 'http://cr-dar.cranecloud.africa/render?target=102_134_147_244_5001.Network.T&format=json'

# 90, 95 and 99
def get_percentiles(array_values,nth):
    print(nth, "th percentile is: ", np.percentile(array_values,nth))
    return True

def get_modal(array_values):
    array = np.array(array_values)
    mode = stats.mode(array,keepdims=True)
    print("Modal mark is: ", mode.mode[0])

def get_average(array_values):
    array = np.array(array_values)
    print("Average mark is: ", np.average(array))

def get_values(url):
    # emulate source of the metrics
    response = requests.get(url)
    latency_values =[]
    if response.status_code == 200:
        data = response.json()
        latency_values = data[0]['datapoints']
        #print(data[0]['datapoints'])
    else:
        print(f'Request failed with status code {response.status_code}')

    result = []
    for item in latency_values:
        if item[0] is not None:
            result.append(item[0])
    print(result)
    return result



if __name__ == "__main__":
    print("----------latency-----------")
    latency_array = get_values(latency_url)
    print("---/|\----")
    get_percentiles(latency_array,90)
    get_percentiles(latency_array,95)
    get_percentiles(latency_array,5)
    get_modal(latency_array)
    get_average(latency_array)
    print("----------jitter-----------")
    jitter_array = get_values(jitter_url)
    print("---/|\----")
    get_percentiles(jitter_array,90)
    get_percentiles(jitter_array,95)
    get_percentiles(jitter_array,5)
    get_modal(jitter_array)
    get_average(jitter_array)
    print("----------throughput-----------")
    throughput_array = get_values(throughput_url)
    print("---/|\----")
    get_percentiles(throughput_array,90)
    get_percentiles(throughput_array,95)
    get_percentiles(throughput_array,5)
    get_modal(throughput_array)
    get_average(throughput_array)
    
