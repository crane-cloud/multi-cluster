from kubernetes import client, config

config.load_kube_config()
api = client.CustomObjectsApi()
k8s_nodes = api.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")

for stats in k8s_nodes['items']:
    print("Node Name: %s\tCPU: %s\tMemory: %s" % (stats['metadata']['name'], stats['usage']['cpu'], stats['usage']['memory']))
