import random
import threading
import time
from jsonrpcserver import Success, method, serve, InvalidParams, Result, Error
import requests
import json
from util import retrieve_clusters_info
from timer import BaseTimer
import socket
import os
import asyncio
import aiohttp
from le import Cluster

#-----------------------------#
# The following are jsonrpcserver RPC methods (@method) that a peer can invoke
@method
def requestVote(member_id: str, proposal_number: int) -> Result:
    #At the receipt of requestVote, the member state is changed to voter

    print("Entering voter method")

    response = Cluster.voter(self, proposal_number, member_id)

    result = {"response": response, "message": "Success", "status": 200}

    return Success(result)

@method
def ackVote(self, member_id: str, proposal_number: int):
    #A voter or member receives the ackVote message as confirmation of winner (leader)
    self.leader = {"proposal_number": proposal_number, "voted": member_id}
    return None


@method
def responseVote(message):
    #Message sent to a member as a vote
    return None


@method
def informMember(proposal_number, leader_id):
    #If a member receives this message (should be from the leader), the leaderShipTermTimer is reset
    return None

@method
def pollLeader() -> Result:
    # Candidate can always poll the leader 
    return None
 

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
port = int(os.getenv("LE_PORT", 5002))

if __name__ == "__main__":
    while True:
        print("Starting LE Service on {ip_address}:{port}".format(ip_address=ip_address, port=port))
        serve(ip_address, port)