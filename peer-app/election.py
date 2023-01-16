#starting point of leader comparison to select a leader


def choose_network_leader(metrics):
    number_of_cluster = len(metrics)
    #set better to first element first latency
    better_cluster_id = metrics[0][1]
    better_cluster_latency = metrics[0][3]

    for i in range(number_of_cluster):
        if metrics[i][3] < better_cluster_latency:
            better_cluster_id = metrics[i][1]
    
    print("selected cluster:")
    print(better_cluster_id)
    return better_cluster_id

