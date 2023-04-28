import random
import threading
import logging
import time
from jsonrpcserver import Success, method, serve, dispatch, InvalidParams, Result, Error, methods
import requests
import json
from util import retrieve_clusters_info
from timer import BaseTimer
import socket
import os
import asyncio
import aiohttp
from flask import Flask, request, Response


app = Flask(__name__)

REQUESTVOTETIMER = 50
RESPONSEVOTETIMER = 50
LEADERSHIPVOTETIMER = 50
LEADERSHIPTERMTIMER = 60
POLLLEADERTIMER = 100

RESPONSETIMEOUT = 30

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
port = int(os.getenv("LE_PORT", 5002))

class Cluster:
    # The initial state of a cluster member (the member may eventually take on the roles of voter, leader or candidate)
    def __init__(self, member_id, members):
        self.member_id = member_id # unique identifier of the member (address & port)
        self.members = members # cluster info as per the view {A dictionary of the cluster members}
        self.state = 'member' # initial state of member
        self.proposal_number = 0 # the initial proposal number
        self.voted = {} # who this member has voted
        self.leaderx = {} # the leader information at this member

        self.election_timeout = random.randint(50, 70) / 10.0 #seconds
        self.heartbeat_interval = 30 #seconds
        self.leadership_timer = None

        self.election_timer = None

    # We perform a set of functions based on the state of the cluster
    def run(self):
        print('Run Mode')
        while True:
            if self.state == 'member':
                asyncio.run(cluster.member())
            elif self.state == 'leader':
                print("Entering Leader Role")
                asyncio.run(self.leader())
            elif self.state == 'candidate':
                asyncio.run(self.candidate())
            else:
                print('We are in an unknown state')
                sys.exit(1)

    # A function to reset the leadership timer
    def reset_leadership_timer(self):
        print("Resetting the leadership timer")
        if self.leadership_timer:
            self.leadership_timer.cancel()
        self.leadership_timer = threading.Timer(self.election_timeout, self.start_election_cycle(self.proposal_number))
        self.leadership_timer.start()


    async def start_election_cycle(self, proposal_number):
        #print("A new election cycle has started")

        self.proposal_number = proposal_number + 1
        self.votes = {self.proposal_number: []}
        leader_size = len(self.members) // 2 + 1

        print("A new election cycle has started with proposal {proposal} at time {ts}".format(proposal=self.proposal_number, ts=time.time()))

        payload = {
            "method": "requestVote",
            "params": {
                "self": None,
                "member_id": self.member_id,
                "proposal_number": self.proposal_number
                },
            "jsonrpc": "2.0",
            "id": 1,
            }
        print(payload)

        async with aiohttp.ClientSession() as session:
            tasks = []
            for member in self.members:
                #Set the requestVoteTimer
                try:
                    task = asyncio.create_task(make_post_request(member["cluster_id"], payload, RESPONSETIMEOUT))
                    tasks.append(task)
                except asyncio.TimeoutError:
                    print(f"Timeout Error: {member['cluster_id']}")
                    continue
            responses = await asyncio.gather(*tasks)

        for response in responses:
            if (response is not None) and (response["result"]):

                print("It seems we received a vote! Let us confirm it")

                vote_response = response["result"]["response"]
                vote_params = response["result"]["params"]

                if vote_response == "responseVote":
                    if self.proposal_number == vote_params[1]:
                        print("Yay! - A valid vote from {idx} for proposal {proposal}".format(idx=vote_params[0], proposal=vote_params[1]))

                        #Confirm it is not a duplicate vote
                        if vote_params[0] not in self.votes[self.proposal_number]:
                            self.votes[self.proposal_number].append(vote_params[0])
                
                #A possible different message or just an invalid vote
                else:
                    print("Dang, it is an invalid vote :(")
                    continue

        print("Number of votes received: {votes}".format(votes=len(self.votes[self.proposal_number])))

        if len(self.votes[self.proposal_number]) >= leader_size:
            #We can now execute the leader role functions - send ackVote
            self.state = 'leader'
        else:
            print("Async operation should proceed")
           # self.state = 'member'
            
        #else:
        #    # We expect another node (especially the candidates) to start LE
        #    if not (self.leaderx):
        #        print('We start a new election cycle with a new proposal number')
        #       #self.state = 'member'
        #    else:
        #        print("I have a leader with ID {idx} at propsal {proposal}".format(idx = self.leaderx["leader"], proposal = self.leaderx["proposal_number"]))
        #
        #        # Update the member proposal number to the latest for future elections
        #        self.proposal_number = self.leaderx["proposal_number"]             
        #        #self.state = 'member'


    async def member(self):

        print('Member Role with proposal number: {proposal}'.format(proposal=self.proposal_number))
        print("Thread name:", threading.current_thread().name)

        # We wait for a random amount of time - there could be a leader soon
        time.sleep(random.randint(50,150)/10)


        if self.leaderx:
            print("I have self leaderx: {rx}".format(rx=self.leaderx["leader"]))

        if cluster.leaderx:
            print("I have cluster leaderx: {rx}".format(rx=cluster.leaderx["leader"]))

        if self.leaderx or cluster.leaderx:

            print("I have a leader with ID {idx} at propsal {proposal}".format(idx = self.leaderx["leader"], proposal = self.leaderx["proposal_number"]))

            # Update the member proposal number to the latest for future elections
            self.proposal_number = self.leaderx["proposal_number"]
            print("Updated proposal from leader entry: {proposal}".format(proposal=self.leaderx["proposal_number"]))            


        else:
            # We start a new election cycle
            print("How come no valid leader here?")
            await (self.start_election_cycle(self.proposal_number))


            # We reset the leadership timer
            # rl = await self.reset_leadership_timer()

        print("We enter a 6s sleep")

        time.sleep(6)
        # We start a new election cycle
        #election_cycle = await (self.start_election_cycle())



    async def start_heartbeat(self):
        print("In the start_heartbeat")
        payload_inf = {
            "method": "informMember",
            "params": {
                "self": None,
                "leader_id": self.member_id,
                "proposal_number": self.proposal_number
                },
            "jsonrpc": "2.0",
            "id": 2,
            }

        
        while True:

            if self.state == 'leader' and cluster.state == 'leader':

                print("Sending heartbeat with {payload}".format(payload=payload_inf))

                async with aiohttp.ClientSession() as session:
                    tasks = []
                    for member in self.members:
                        try:
                            task = asyncio.create_task(make_post_request(member["cluster_id"], payload_inf, RESPONSETIMEOUT))
                            tasks.append(task)
                        except asyncio.TimeoutError:
                            print(f"Timeout Error: {member['cluster_id']}")
                            continue
                    responses = await asyncio.gather(*tasks)

                    print(responses)

                # We sleep for the heartbeat interval & then send another heartbeat
                time.sleep(self.heartbeat_interval)
            else:
                print("Not a leader")
                break



    def voter(self, member_id, proposal_number):
        
        print('Voter Method')

        voter_id = cluster.member_id

        print("Received vote request from {member} with proposal {proposal}".format(member=member_id, proposal=proposal_number))

        response_ack = {
            "response": "responseVote",
            "params": [voter_id, proposal_number],
        }

        # Fixes a bug on the dispatcher method of jsonrpcserver
        response_nack = {
            "response": "noVote",
            "params": [voter_id, proposal_number],
        }

        # If never voted or received a leader result
        if not(cluster.voted)  and not(cluster.leaderx):
            try:
                print("Seems we have not voted before")
                cluster.voted = {"proposal_number": proposal_number, "voted": member_id}
                return response_ack
            except:
                return None

        # If the cluster has better leader information
        elif cluster.voted:
            if proposal_number > cluster.voted['proposal_number']:
                try:
                    print("A better proposal {proposal} than voted {v} from {idx}".format(proposal=proposal_number, v=cluster.voted['proposal_number'], idx=member_id))
                    cluster.voted = {"proposal_number": proposal_number, "voted": member_id}
                    return response_ack
                except:
                    return None
            else:
                return response_nack


        # If the cluster voted, confirm this is a fresh election
        elif cluster.leaderx:
            #print("Received leader {leader} info before with better proposal {proposal} than {l}".format(leader=cluster.leaderx['leader'], proposal=cluster.leaderx['proposal_number'], l=proposal_number))

            if proposal_number > cluster.leaderx['proposal_number']:
                try:
                    print("A better proposal {proposal} than in leaderx {lx} from {idx}".format(proposal=proposal_number, lx=cluster.leaderx['proposal_number'], idx=member_id))
                    cluster.voted = {"proposal_number": proposal_number, "voted": member_id}
                    return response_ack
                except:
                    return None
            else:
                return response_nack

        else:
            return response_nack

 

    async def leader(self):
        print('Leader Role')
        #As a leader, send ackVote message to all the members

        print("As leader, this is my ID: {idx} and proposal number: {proposal}".format(idx=self.member_id, proposal=self.proposal_number))

        payload_ack = {
            "method": "ackVote",
            "params":{
                "self": None,
                "member_id": self.member_id,
                "proposal_number": self.proposal_number
                },
            "jsonrpc": "2.0",
            "id": 3,
            }

        print(payload_ack)

        async with aiohttp.ClientSession() as session:
            tasks = []
            for member in self.members:
                try:
                    task = asyncio.create_task(make_post_request(member["cluster_id"], payload_ack, RESPONSETIMEOUT))
                    tasks.append(task)
                except asyncio.TimeoutError:
                    print(f"Timeout Error: {member['cluster_id']}")
                    break
            responses_ack = await asyncio.gather(*tasks)

        print("As leader we need to send heartbeat messages")

        try:
            #heartbeat_logger = logging.getLogger('heartbeat')
            #heartbeat_logger.setLevel(logging.INFO)
            #handlerb = logging.StreamHandler()
            #handlerb.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
            #heartbeat_logger.addHandler(handlerb)

            self.leadership_timer = None
            tx = await self.start_heartbeat()

            #heartbeat_thread = threading.Thread(target=self.start_heartbeat)
            #heartbeat_thread.daemon = True
            #heartbeat_thread.start()
        
        except Exception as e:
            print(f"Error: {e}")

        print("Do we get here, let us sleep for 5sec")
        time.sleep(5)


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
    def requestVote(self, member_id, proposal_number) -> Result:
        #At the receipt of requestVote, the member state is changed to voter

        print("requestVote request from member: {member} with proposal: {proposal}".format(member=member_id, proposal=proposal_number))
    
        result = Cluster.voter(self, member_id, proposal_number)

        #result = {"response": "responseVote", "message": "Success", "status": 200}
   
        if result:
            print("Now providing a responseVote or noVote to client")
            print(result)
            return Success(result)
        else:
            return None

    @method
    def ackVote(self, member_id, proposal_number):
        #A voter or member receives the ackVote message as confirmation of winner (leader)

        print("Cluster state at ackVote {ack}".format(ack=cluster.state))
        cluster.leaderx = {"proposal_number": proposal_number, "leader": member_id}

        #For future elections, we update our proposal number
        cluster.proposal_number = proposal_number

        print("Updated my proposal number to: {proposal}".format(proposal=cluster.leaderx["proposal_number"]))

        print("I have a new leader {leader} (voted or not) with proposal {proposal}!".format(leader=cluster.leaderx["leader"], proposal=cluster.leaderx["proposal_number"]))

        response = {
            "response": "ackEd",
            "params": [cluster.leaderx["leader"], cluster.leaderx["proposal_number"]],
        }

        #Not a very useful response as it is not required - we could write another post for these kind of messages

        # Only change the state of the member not leader

        if cluster.member_id != member_id:
            cluster.state = "member"


        return Success(response)


    @method
    def responseVote(message):
        #Message sent to a member as a vote
        return None


    @method
    def informMember(self, leader_id, proposal_number):
        #If a member receives this message (should be from the leader), the leaderShipTermTimer is reset

        print("Received the informMember message")

        print("The leader {leader} with proposal {proposal} is Alive".format(leader=leader_id, proposal=proposal_number))
        ##cluster.reset_leadership_timer()

        cluster.leaderx["leader"] = leader_id

        if leader_id != cluster.member_id:
            print("I am strictly a member")

            cluster.state = 'member'

        return Success(None)

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
            resp = await asyncio.wait_for(session.post(url, data=json.dumps(payload), headers=headers), timeout=timeout)

            latency = time.monotonic() - start_time
            print(f"Request to {url} completed in {latency:.4f} seconds")

            try:
                return (await resp.json())
            except Exception as e:
                print(f"Error: {e}")
                return None

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




# This retrieves members of the distributed system [Can be provided to any of the roles]
##members = retrieve_clusters_info()

members = [{'name': 'peer_hp070', 'ip_address': '128.110.218.109', 'port': 5002, 'cluster_id': '128.110.218.109:5002'},
           {'name': 'peer_hp076', 'ip_address': '128.110.218.115', 'port': 5002, 'cluster_id': '128.110.218.115:5002'}]

member_id = ip_address + ':' + str(port)

try:
    cluster = Cluster(member_id, members)
    print("Successfully created cluster")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)


# JSON-RPC routes
@app.route('/', methods=['POST'])
def index():
    req = request.get_data().decode()
    response = dispatch(req)
    return Response(str(response), status=200, mimetype='application/json')


if __name__ == '__main__':

    # Create a logger for the cluster thread
    cluster_logger = logging.getLogger('cluster')
    cluster_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    cluster_logger.addHandler(handler)

    #print(cluster.state)
    #print(cluster.proposal_number)
    #print(cluster.member_id)

    # Configure Flask's own logging
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    print("Starting the cluster thread")
    cluster_thread = threading.Thread(target=cluster.run)
    cluster_thread.daemon = True
    cluster_thread.start()

    #asyncio.run(cluster.run())

    print("Starting LE Service on {ip_address}:{port}".format(ip_address=ip_address, port=port))
    app.run(debug=True, host = ip_address, port=port)