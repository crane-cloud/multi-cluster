from jsonrpcserver import Success, method
import  requests
from jsonrpclib import Server

import os


@method
def send_profile_to_peers():
    current_url =  os.getenv('HOST'),
    
    #using ports from inside the container
    server1Port = 5100
    server2Port = 5101
    server3Port = 5102
    servers = [
       {'ip': 'cluster-server', 'port': server1Port},
       {'ip': 'cluster-server-2', 'port': server2Port},
       {'ip': 'cluster-server-3', 'port': server3Port}
    ]
    #create peer list
    responses = []
    c = Server("http://cluster-server:5100")
    response = c.peer_message_response(current_url)
    responses.append(response)
    print(responses)
    # for server in servers:
    #     if server['ip'] != current_url:
    #         c = Server("http://"+server["ip"]+":"+str(server['port']))
    #         response = c.peer_message_response(current_url)
    #         responses.append(response)
    # print(responses)


if __name__ == "__main__":
    print('start')
    send_profile_to_peers()


