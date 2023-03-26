# assumming availability is 1, since no availablity data is returned
# computing the profile of cr-dar in relation to all the other profiles

# W1P: 0.4
# W1M: 0.3
# W1D: 0.3
# W1T: 0.4
# W1L: 0.4
# W1J: 0.2
# W1A: 1
# W2R: 0.35
# W2N: 0.45
# W2A: 0.2

class WeightClass:
    #WEIGHTs
    #resources
    def __init__(self):
        self.base_cluster_metrics = {}

    cpu_weight_1 = 0.4
    memory_weight_1 = 0.3
    disk_weight_1 = 0.3
    resource_weight_2 = 0.35
    #network
    throuhput_weight_1 = 0.4
    latency_weight_1 = 0.4
    jitter_weight_1 = 0.2
    network_weight_2 = 0.45
    #availability
    availability_weight_1 = 1
    availability_weight_2 = 0.2

    # our base cluster id
    dr_cluster_ip = '196.32.212.213:5001'
    assumed_availability = 1
    
    
weightInstance = WeightClass()


# test_data =[
#     {
#     "latency": 23.0792,
#     "jitter": 1.1542,
#     "throughput": 435.7958,
#     "cpu": 100.0,
#     "memory": 95.34,
#     "disk": 95.4,
#     "ip": "102.134.147.244:5001"
#     },
#     {
#     "latency": 36.1608,
#     "jitter": 135.34819999999954,
#     "throughput": 625.1694,
#     "cpu": 96.5,
#     "memory": 95.4,
#     "disk": 95.4,
#     "ip": "196.32.215.213:5001"
#     },
#     {
#     "latency": 18,
#     "jitter": 0.3,
#     "throughput": 10,
#     "cpu": 4,
#     "memory": 8192,
#     "disk": 85,
#     "ip": "196.43.171.248:5001"
#     },
#     {
#     "latency": 23,
#     "jitter": 0.5,
#     "throughput": 25,
#     "cpu": 10,
#     "memory": 4096,
#     "disk": 40,
#     "ip": "196.32.212.213:5001"
#     }
# ]
 

def handle_metrics_list(data):
    formated_data =format_matrics_data(data)
    cluster_profiles_in_relation_to_base =[]
    for metric in formated_data:
        network_sumation =  compute_network_profile(metric)
        resource_sumation =   compute_resource_profile(metric)
        availability_sumation =  compute_availability_profile(metric)
        profile = overall_profile(resource_sumation,network_sumation,availability_sumation)
        cluster_profiles_in_relation_to_base.append({
            'based_on_cluster_id': weightInstance.dr_cluster_ip,
            'against_cluster_ip': metric['ip'],
            'network_value':network_sumation,
            'resource_value':resource_sumation,
            'availability_value':availability_sumation,
            'profile': profile
        })

    return cluster_profiles_in_relation_to_base

# remove base cluster data from metrics list
def format_matrics_data(data):
    data_without_base_cluster = []
    for data_item in data:
        if data_item['ip'] != weightInstance.dr_cluster_ip:
            data_without_base_cluster.append(data_item)
        if data_item['ip'] == weightInstance.dr_cluster_ip:
            weightInstance.base_cluster_metrics = data_item
    return data_without_base_cluster

def compute_network_profile(formated_metric):
    throughput = (weightInstance.throuhput_weight_1 * weightInstance.base_cluster_metrics['throughput'])/(formated_metric['throughput'] + weightInstance.base_cluster_metrics['throughput'])
    jitter= (weightInstance.jitter_weight_1 * weightInstance.base_cluster_metrics['jitter'])/(formated_metric['jitter'] + weightInstance.base_cluster_metrics['jitter'])
    latency = (weightInstance.latency_weight_1 * weightInstance.base_cluster_metrics['latency'])/(formated_metric['latency'] + weightInstance.base_cluster_metrics['latency'])
    return throughput + jitter + latency

def compute_resource_profile(formated_metric):
    disk = (weightInstance.disk_weight_1 * weightInstance.base_cluster_metrics['disk'])/(formated_metric['disk'] + weightInstance.base_cluster_metrics['disk'])
    cpu= (weightInstance.cpu_weight_1 * weightInstance.base_cluster_metrics['cpu'])/(formated_metric['cpu'] + weightInstance.base_cluster_metrics['cpu'])
    memory = (weightInstance.memory_weight_1 * weightInstance.base_cluster_metrics['memory'])/(formated_metric['memory'] + weightInstance.base_cluster_metrics['memory'])
    return disk + cpu + memory

def compute_availability_profile(formated_metric):
    return (weightInstance.availability_weight_1*weightInstance.assumed_availability)/(weightInstance.assumed_availability+weightInstance.assumed_availability)

def overall_profile(Resource,Network,Availablity):
    profile = (Resource * weightInstance.resource_weight_2)+(Network * weightInstance.network_weight_2 ) + (Availablity * weightInstance.availability_weight_2 )
    return profile


# if __name__ == "__main__":
#    profiles_list =  handle_metrics_list(test_data)
#    print(profiles_list)