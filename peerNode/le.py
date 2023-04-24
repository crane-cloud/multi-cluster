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


REQUESTVOTETIMER = 50
RESPONSEVOTETIMER = 50
LEADERSHIPVOTETIMER = 50
LEADERSHIPTERMTIMER = 60
POLLLEADERTIMER = 100

class Cluster:
    # The initial state of a cluster member (the member may eventually take on the roles of voter, leader or candidate)
    def __init__(self, member_id, members):
        self.member_id = member_id # unique identifier of the member (address & port)
        self.members = members # cluster info as per the view {A dictionary of the cluster members}
        self.state = 'member' # initial state of member
        self.proposal_number = 0 # the initial proposal number
        #self.leader_size = len(self.members.keys()) // 2 + 1 # quorum size to guarantee leadership
        self.voted = {}
        self.leaderx = {}

    # We perform a set of functions based on the state of the cluster
    def run(self):
        print('We are in the Run Mode')
        while True:
            if self.state == 'member':
                asyncio.run(self.member())
            #elif self.state == 'voter':
            #    self.voter()
            elif self.state == 'leader':
                print("Entering Leader Role")
                asyncio.run(self.leader())
            elif self.state == 'candidate':
                self.candidate()
            else:
                print('We are in an unknown state')
                return None

    async def member(self):

        print('Member Role')

        self.proposal_number += 1
        self.votes = {self.proposal_number: []}# the votes a member receives in election rounds
        self.leaderx = {} # the current leader information at this cluster

        leader_size = len(self.members) // 2 + 1 # quorum size to guarantee leadership

        #print(leader_size)

        payload = {
            "method": "requestVote",
            "params": [self.member_id, self.proposal_number],
            "jsonrpc": "2.0",
            "id": 0,
            }

        print(payload)

        async with aiohttp.ClientSession() as session:
            tasks = []
            for member in self.members:
                #Set the requestVoteTimer
                print(member)
                
                try:
                    task = asyncio.create_task(make_post_request(member["cluster_id"], payload, REQUESTVOTETIMER))
                    tasks.append(task)
                except asyncio.TimeoutError:
                    print(f"Timeout Error: {member['cluster_id']}")
                    continue
            responses = await asyncio.gather(*tasks)
            print(responses)

        for response in responses:
            print(response)
            # We need to check if the responses contain the vote details with a responseVote method
        
        print('We wait for the responseVoteTimer to expire')
        time.sleep(5)
        # We set the responseVoteTimer - we expect the results from all the peers
        # We count the votes at this point (For the latest proposal number, we count the votes)
        # Example: self.votes = {1: {peer1, peer2, peer3}}
        ## - len(self.votes[1] = 3)
        if len(self.votes[self.proposal_number]) >= leader_size:
            #We can now execute the leader role functions - send ackVote
            self.state = 'leader'
            
        else:
            print('We back off for a random bounded time: 10ms - 100ms')
            time.sleep(random.randint(10,100)/10)

            # We expect another node (especially the candidates) to start LE
            if not (self.leaderx):
                print('We start a new election cycle with a new proposal number')
                
                # We may need to pull out the requestVote function - to be easily called?
                # It would be easy to repeat here with just a new proposal number:
                self.state = 'member'    


    def voter(self, proposal_number, member_id):
        print('Voter Method')
        voter_id = self.member_id

        print(voter_id)

        response = {
            "method": "responseVote",
            "params": [voter_id, proposal_number],
        }

        # If never voted or received a leader result
        if not(self.voted)  and not(self.leaderx):
            try:
                self.voted = {"proposal_number": proposal_number, "voted": member_id}
                return response
            except:
                return None
        
        # If the cluster voted, confirm this is a fresh election
        elif self.voted or self.leaderx:
            if proposal_number > self.voted['proposal_number'] or proposal_number > self.leaderx['proposal_number']:
                try:
                    self.voted = {"proposal_number": proposal_number, "voted": member_id}
                    return response
                except:
                    return None
            else:
                return None

        else:
            return None

    async def leader(self):
        print('Leader Role')
        leader_id = member_id
        #As a leader, send ackVote message to all the members

        print(leader_id)

        payload_ack = {
            "method": "ackVote",
            "params": [self.member_id, self.proposal_number],
            "jsonrpc": "2.0",
            "id": 0,
            }

        print(payload_ack)

        async with aiohttp.ClientSession() as session:
            tasks = []
            for member in self.members:
                #Set the requestVoteTimer
                print(member)
                
                try:
                    task = asyncio.create_task(make_post_request(member["cluster_id"], payload_ack, LEADERSHIPVOTETIMER))
                    tasks.append(task)
                except asyncio.TimeoutError:
                    print(f"Timeout Error: {member['cluster_id']}")
                    break
            responses_ack = await asyncio.gather(*tasks)
            print(responses_ack)

        time.sleep(LEADERSHIPTERMTIMER)

    def candidate(self):
        print('We are in the candidate role')
        #We arrive here as a result of one of the profiles better than some proposal profile
        candidate_id = self.member_id

        #We set the LeadershipVoteTimer [We expect a leader within this time]
        #If this expires, and there is no ackVote message - we begin an election phase

        # If within this period, we receive an ackVote and subsequent leader update - we revert to the member role

        # Or we remain with this role, and keep polling the leader to ensure it is live - increased chances of taking over
    


    #-----------------------------#
    # The following are jsonrpcserver RPC methods (@method) that a peer can invoke
    @method
    def requestVote(self, member_id: str, proposal_number: int) -> Result:
        #At the receipt of requestVote, the member state is changed to voter

        print("Entering voter method")
        #self.state = 'voter'

        response = voter(self, member_id, proposal_number)

        result = {"response": response, "message": "Success", "status": 200}

        return result

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
    

async def make_post_request(peer_id, payload, timeout):
    # Send the message to the specified peer
    url = "http://"+peer_id
    headers = {'content-type': 'application/json'}

    async with aiohttp.ClientSession() as session:
        start_time = time.monotonic()
        try:
            print(f"Sending post request to {url}")
            response = await asyncio.wait_for(session.post(url, data=json.dumps(payload), headers=headers), timeout=timeout)
            latency = time.monotonic() - start_time
            print(f"Request to {url} completed in {latency:.4f} seconds")
            return response

        except asyncio.TimeoutError:
            print(f"Timeout error for server {url}")
            latency = time.monotonic() - start_time
            print(f"Request to {url} timeout error in {latency:.4f} seconds")
            return None
        except aiohttp.ClientError:
            print(f"Client error for server {url}")
            return None
        except aiohttp.client_exceptions.ClientConnectorError:
            print(f"Connection error for server {url}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None







hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
port = int(os.getenv("LE_PORT", 5002))

if __name__ == '__main__':

    serve(ip_address, port)

    # This retrieves members of the distributed system [Can be provided to any of the roles]
    ##members = retrieve_clusters_info()

    members = [{'name': 'peer_hp070', 'ip_address': '128.110.218.109', 'port': 5002, 'cluster_id': '128.110.218.109:5002'}, 
                {'name': 'peer_hp076', 'ip_address': '128.110.218.115', 'port': 5002, 'cluster_id': '128.110.218.115:5002'}]

    member_id = ip_address + ':' + str(port)

    cluster = Cluster(member_id, members)
    # We start the cluster with a member role
    print(cluster.state)
    print(cluster.proposal_number)
    print(cluster.member_id)

    asyncio.run(cluster.run())