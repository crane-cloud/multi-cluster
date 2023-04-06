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
    dr_cluster_ip = '196.32.212.213:5001'
    #assumed_availability = 1

    #Network target values
    Latence_target = 24
    Jitter_target = 3.26
    Throughput_target = 894

    
    
weightInstance = WeightClass()

def handle_metrics_list(data):
    formated_data =format_matrics_data(data)
    cluster_profiles_in_relation_to_base =[]
    for metric in formated_data:
        # network_sumation =  compute_network_profile(metric)
        network_sumation = compute_network_profile_using_targets(metric)
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
    throughput = (weightInstance.W1T * weightInstance.base_cluster_metrics['throughput'])/(formated_metric['throughput'] + weightInstance.base_cluster_metrics['throughput'])
    jitter= (weightInstance.W1J * weightInstance.base_cluster_metrics['jitter'])/(formated_metric['jitter'] + weightInstance.base_cluster_metrics['jitter'])
    latency = (weightInstance.W1L * weightInstance.base_cluster_metrics['latency'])/(formated_metric['latency'] + weightInstance.base_cluster_metrics['latency'])
    return throughput + jitter + latency

def compute_network_profile_using_targets(formated_metric):
    throughput = (weightInstance.W1T * formated_metric['throughput'])/(formated_metric['throughput'] + weightInstance.Throughput_target)
    jitter= (weightInstance.W1J * weightInstance.Jitter_target)/(formated_metric['jitter'] + weightInstance.Jitter_target)
    latency = (weightInstance.W1L * weightInstance.Latence_target)/(formated_metric['latency'] + weightInstance.Latence_target)
    return throughput + jitter + latency

def compute_resource_profile(formated_metric):
    disk = (weightInstance.W1D * weightInstance.base_cluster_metrics['disk'])/(formated_metric['disk'] + weightInstance.base_cluster_metrics['disk'])
    cpu= (weightInstance.W1P * weightInstance.base_cluster_metrics['cpu'])/(formated_metric['cpu'] + weightInstance.base_cluster_metrics['cpu'])
    memory = (weightInstance.W1M * weightInstance.base_cluster_metrics['memory'])/(formated_metric['memory'] + weightInstance.base_cluster_metrics['memory'])
    return disk + cpu + memory

def compute_availability_profile(formated_metric):
    return (weightInstance.W1A*weightInstance.base_cluster_metrics['availability'])/(weightInstance.base_cluster_metrics['availability']+formated_metric['availability'])

def overall_profile(Resource,Network,Availablity):
    profile = (Resource * weightInstance.W2R)+(Network * weightInstance.W2N ) + (Availablity * weightInstance.W2A )
    return profile


# if __name__ == "__main__":
#    profiles_list =  handle_metrics_list(test_data)
#    print(profiles_list)