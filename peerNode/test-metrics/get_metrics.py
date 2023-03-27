import requests

## assuming we are on cr-dar, base url
base_url = 'http://cr-dar.cranecloud.africa/render'

def clean_metrics_data(data):
    result = []
    for item in data:
        if item[0] is not None:
            result.append(item[0])
    #print(result)
    return result

def get_network_latency(ip):
    fomatted_ip = ip.replace('.','_').replace(':','_')
    response = requests.get(f"{base_url}?target={fomatted_ip}.Network.L&format=json")
    values =[]
    if response.status_code == 200:
        data = response.json()
        values = data[0]['datapoints']
        #print(data[0]['datapoints'])
        return clean_metrics_data(values)
    else:
        print(f'Latency Request failed with status code {response.status_code}')
        return values


def get_network_jitter(ip):
    fomatted_ip = ip.replace('.','_').replace(':','_')
    response = requests.get(f"{base_url}?target={fomatted_ip}.Network.J&format=json")
    values =[]
    if response.status_code == 200:
        data = response.json()
        values = data[0]['datapoints']
        #print(data[0]['datapoints'])
        return clean_metrics_data(values)
    else:
        print(f'Jitter Request failed with status code {response.status_code}')
        return values

def get_network_throughput(ip):
    fomatted_ip = ip.replace('.','_').replace(':','_')
    response = requests.get(f"{base_url}?target={fomatted_ip}.Network.T&format=json")
    values =[]
    if response.status_code == 200:
        data = response.json()
        values = data[0]['datapoints']
        #print(data[0]['datapoints'])
        return clean_metrics_data(values)
    else:
        print(f'Throughput Request failed with status code {response.status_code}')
        return values

def get_cpu(ip):
    fomatted_ip = ip.replace('.','_').replace(':','_')
    response = requests.get(f"{base_url}?target={fomatted_ip}.Resource.P&format=json")
    values =[]
    if response.status_code == 200:
        data = response.json()
        values = data[0]['datapoints']
        #print(data[0]['datapoints'])
        return clean_metrics_data(values)
    else:
        print(f'Cpu Request failed with status code {response.status_code}')
        return values

def get_memory(ip):
    fomatted_ip = ip.replace('.','_').replace(':','_')
    response = requests.get(f"{base_url}?target={fomatted_ip}.Resource.M&format=json")
    values =[]
    if response.status_code == 200:
        data = response.json()
        values = data[0]['datapoints']
        #print(data[0]['datapoints'])
        return clean_metrics_data(values)
    else:
        print(f'Memory Request failed with status code {response.status_code}')
        return values

def get_disk(ip):
    fomatted_ip = ip.replace('.','_').replace(':','_')
    response = requests.get(f"{base_url}?target={fomatted_ip}.Resource.D&format=json")
    values =[]
    if response.status_code == 200:
        data = response.json()
        values = data[0]['datapoints']
        #print(data[0]['datapoints'])
        return clean_metrics_data(values)
    else:
        print(f'Latency Request failed with status code {response.status_code}')
        return values

def get_availability(ip):
    fomatted_ip = ip.replace('.','_').replace(':','_')
    response = requests.get(f"{base_url}?target={fomatted_ip}.Availability.A&format=json")
    values =[]
    if response.status_code == 200:
        data = response.json()
        values = data[0]['datapoints']
        #print(data[0]['datapoints'])
        return clean_metrics_data(values)
    else:
        print(f'Latency Request failed with status code {response.status_code}')
        return values