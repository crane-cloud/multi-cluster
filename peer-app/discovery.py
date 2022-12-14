import random
import string
import os
import requests


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def generate_cluster_info():
    cluster_info = {"cluster_id": random.randint(000000000, 9999999999),
                    "name": f"clt-{os.getenv('CLUSTER_NAME', get_random_string(4))}",
                    "ip_address": "127.0.0.1",
                    "port": os.getenv('PORT', 5141)}
    print(cluster_info)
    return cluster_info


def request_to_join_network():
    url = f"{os.getenv('CENTRAL_SERVER_LINK')}/clusters"
    # url = "http://localhost:5500/clusters"
    payload = generate_cluster_info()
    print(payload)
    try:
        respose = requests.post(url, data=payload)
        if respose.status_code == 409:
            print("Cluster already exists")
            print(respose.data)
            return False
        elif respose.status_code == 201:
            print("Successfully joined network")
            return True
        else:
            print("Error joining network")
            print(dir(respose))
            return False
    except Exception as e:
        print("Error: ", e)
        return False
