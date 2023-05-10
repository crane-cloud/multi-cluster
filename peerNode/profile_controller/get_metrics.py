import requests
import socket

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

base_url = "http://" + ip_address + "/render"

def clean_metrics_data(data):
    result = []
    for item in data:
        if item[0] is not None:
            result.append(item[0])
    return result

def generic_get_metrics(ip, metric_name):
    fomatted_ip = ip.replace('.','_').replace(':','_')
    response = requests.get(f"{base_url}?target={fomatted_ip}.{metric_name}&format=json&from=-7d")
    values =[]
    if response.status_code == 200:
        data = response.json()
        values = data[0]['datapoints']
        return clean_metrics_data(values)
    else:
        print(f'{metric_name} Request failed with status code {response.status_code}')
        return values


def getp_value(ip, metric_name):
    fomatted_ip = ip.replace('.','_').replace(':','_')
    response = requests.get(f"{base_url}?target=nPercentile({fomatted_ip}.{metric_name},95)&format=json&from=-7d")
    values =[]
    if response.status_code == 200:
        data = response.json()
        #since all values here are similar, we simply pick the first value
        values = data[0]['datapoints']
        #print(data[0]['datapoints'])
        singleValueArray = clean_metrics_data(values)
        return singleValueArray[0]
    else:
        print(f'Latency Request failed with status code {response.status_code}')
        return values


def get_availability(ip):
    fomatted_ip = ip.replace('.','_').replace(':','_')
    response = requests.get(f"{base_url}?target=averageSeries({fomatted_ip}.Availability.A)&format=json&from=-7d")
    values =[]
    if response.status_code == 200:
        data = response.json()
        values = data[0]['datapoints']
        return clean_metrics_data(values)
    else:
        print(f'Fetch request failed with status code {response.status_code}')
        return values