import socket

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

class WeightClass:
    def __init__(self):
        self.base_cm = {}

    W1P = 0.4
    W1M = 0.3
    W1D = 0.3
    W2R = 0.35
    #network
    W1T = 0.4
    W1L = 0.4
    W1J = 0.2
    W2N = 0.45
    #availability
    W1A = 1
    W2A = 0.2

    # our base cluster id
    base = ip_address + ":5001"

    #Network target values
    l_t = 24
    j_t = 3.26
    t_t = 894

    
wObj= WeightClass()

def handle_metrics_list(data):
    formated_data = format_metrics_data(data)
    cluster_profiles = []
    for metric in formated_data:
        np = compute_np(metric)
        rp = compute_rp(metric)
        ap = compute_ap(metric)
        profile =  profile(rp, np, ap)
        cluster_profiles.append({
            'base': wObj.base,
            'target': metric['ip'],
            'n':np,
            'r':rp,
            'a':ap,
            'profile': profile
        })

    return cluster_profiles

# remove base cluster data from metrics list
def format_metrics_data(data):
    data__base = []
    for item in data:
        if item['ip'] != wObj.base:
           data_base.append(item)
        if item['ip'] == wObj.base:
            wObj.base_cm = data_item
    return data__base

def compute_np(metric):
    t = (wObj.W1T * metric['throughput'])/(metric['throughput'] + wObj.t_t)
    j = (wObj.W1J * wObj.j_t)/(metric['jitter'] + wObj.j_t)
    l = (wObj.W1L * wObj.l_t)/(metric['latency'] + wObj.l_t)
    return t + l + j

def compute_rp(metric):
    d = (wObj.W1D * wObj.base_cm['disk'])/(metric['disk'] + wObj.base_cm['disk'])
    p = (wObj.W1P * wObj.base_cm['cpu'])/(metric['cpu'] + wObj.base_cm['cpu'])
    m = (wObj.W1M * wObj.base_cm['memory'])/(metric['memory'] + wObj.base_cm['memory'])
    return d + p + m

def compute_ap(metric):
    return (wObj.W1A*wObj.base_cm['availability'])/(wObj.base_cm['availability']+metric['availability'])

def profile(r, n, a):
    profile = (r * wObj.W2R) + (n * wObj.W2N ) + (a * wObj.W2A)
    return profile