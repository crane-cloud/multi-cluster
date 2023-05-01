import random
import threading
import logging
import time
from jsonrpcserver import Success, method, serve, dispatch, InvalidParams, Result, Error, methods
import requests
import json
import socket
import os
import asyncio
import aiohttp
from flask import Flask, request, Response
import datetime


ELECTIONTIMEOUT = 0.0005 #seconds
RESPONSETIMEOUT = 0.0004 #seconds

app = Flask(__name__)


hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
port = int(os.getenv("LE_PORT", 5002))


class Cluster:
    # The initial state of a cluster member (the member may eventually take on the roles of voter, leader or candidate)
    def __init__(self, member_id, state, members):
        self.member_id = member_id # unique identifier of the member (address & port)
        self.members = members # cluster info as per the view {A dictionary of the cluster members}
        self.state = state # initial state of member
        self.proposal_number = 0 # the initial proposal number
        self.voted = {} # who this member has voted
        self.leaderx = {} # the leader information at this member

        self.election_timeout = 0.0005 #seconds
        self.heartbeat_interval = 0.0003 #seconds
        self.leadership_timer = None

    # We perform a set of functions based on the state of the cluster
    def run(self):
        print('Run Mode with thread {thread}'.format(thread=threading.current_thread().name))
        while True:
            print("Current State: {state}".format(state=self.state))
            if self.state == 'member':
                asyncio.run(self.member())
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
        print("Resetting the leadership timer - received informMember")
        if self.leadership_timer:
            self.leadership_timer.cancel()
        self.leadership_timer = threading.Timer(self.election_timeout, lambda: None)
        self.leadership_timer.start()


    async def async_op(self, payload):
        print("An async Op")
        async with aiohttp.ClientSession() as session:
            tasks = []
            for member in self.members:

                # Only request for votes from other members
                if member["cluster_id"] != self.member_id:
                    try:
                        task = asyncio.create_task(make_post_request(member["cluster_id"], payload, RESPONSE_TIMEOUT))
                        tasks.append(task)
                    except asyncio.TimeoutError:
                        print(f"Timeout Error: {member['cluster_id']}")
                        continue
                else:
                    print("Can't vote, I am requesting for votes!")
            responses = await asyncio.gather(*tasks)
        
        print("Printing response from post request in async_op")
        print(responses)

        return responses


    async def start_election_cycle(self, proposal_number):

        self.proposal_number = proposal_number + 1
        self.votes = {self.proposal_number: []}
        leader_size = len(self.members) // 2 + 1  #to add + 1 with at least 3 nodes

        print("A new election cycle started with proposal {proposal} at time {ts}".format(proposal=self.proposal_number, ts=time.time()))

        with open('/tmp/eval_da.txt', 'a') as fps:
                fps.write("Election: {member} with proposal {proposal} at {ts}\n".format(member=self.member_id, proposal=self.proposal_number, ts=datetime.datetime.now().strftime("%M:%S.%f")[:-2]))


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

        responses = await asyncio.wait_for(self.async_op(payload), timeout=RESPONSETIMEOUT)
        #responses = await self.async_op(payload)

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
                        else:
                            print("Dang, it is a duplicate vote :(")
                            continue
                    else:
                        print("Dang, it is an invalid proposal number :(")
                        continue
                
                #A possible different message or just an invalid vote
                else:
                    print("Dang, it is an invalid vote or response:(")
                    continue

        print("Number of votes received: {votes}".format(votes=len(self.votes[self.proposal_number])))

        if len(self.votes[self.proposal_number]) >= leader_size:
            #We can now execute the leader role functions - send ackVote

            with open('/tmp/eval_da.txt', 'a') as fpx:
                fpx.write("Leader: {leader} with proposal {proposal} at {ts}\n".format(leader=self.member_id, proposal=self.proposal_number, ts=datetime.datetime.now().strftime("%M:%S.%f")[:-2]))

            self.state = 'leader'
        else:
            return None
            #print("We restart the election cycle as member at next proposal {proposal} \n\n\n".format(proposal=(self.proposal_number + 1)))
            self.state = 'member'


    async def member(self):

        print('\n\n\nMember Role with proposal number: {proposal} at time {ts}'.format(proposal=self.proposal_number, ts=time.time()))
        print("Thread name:", threading.current_thread().name)

        # We wait for a random amount of time - there could be a leader soon
        time.sleep(round(random.uniform(0.0001, 0.0004), 6)) # seconds latency range


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
            with open('/tmp/eval_da.txt', 'a') as fpm:
                fpm.write("noLeader: {member} with proposal {proposal} at {ts}\n".format(member=self.member_id, proposal=self.proposal_number, ts=datetime.datetime.now().strftime("%M:%S.%f")[:-2]))            

        # Check if first instance/run
        if self.leadership_timer is None:
            # We start a new election cycle
            print("No leaderx, so we start a new election cycle")
            await asyncio.wait_for(self.start_election_cycle(self.proposal_number), timeout=ELECTIONTIMEOUT) # within the largest latency range

        elif self.leadership_timer and self.leadership_timer.is_alive():
            print("Leadership timer set to expire in", self.leadership_timer.interval, "seconds")

        else:
            print("Leadership timer has already expired - leader dead?")
            with open('/tmp/eval_da.txt', 'a') as fpx:
                fpx.write("Expired: {leader} with proposal {proposal} at {ts}\n".format(leader = self.leaderx["leader"], proposal = self.leaderx["proposal_number"], ts=datetime.datetime.now().strftime("%M:%S.%f")[:-2]))

            await asyncio.wait_for(self.start_election_cycle(self.proposal_number), timeout=ELECTIONTIMEOUT)


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

                print("\n\nSending heartbeat with {payload}".format(payload=payload_inf))

                async with aiohttp.ClientSession() as session:
                    tasks = []
                    for member in self.members:
                        # Only request for votes from other members
                        if member["cluster_id"] != self.member_id:                        
                            try:
                                task = asyncio.create_task(make_post_request(member["cluster_id"], payload_inf, RESPONSETIMEOUT))
                                tasks.append(task)
                            except asyncio.TimeoutError:
                                print(f"Timeout Error: {member['cluster_id']}")
                                continue
                        else:
                            print("I am the leader, no need for informMember")
                    responses = await asyncio.gather(*tasks)

                    print(responses)

                # We sleep for the heartbeat interval & then send another heartbeat
                time.sleep(self.heartbeat_interval)
            else:
                print("Not a leader\n\n")
                break



    def voter(self, member_id, proposal_number):
        
        print('\n\nVoter Method')

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
        print("Vote step checks request: {req} and ours: {ours}".format(req=proposal_number, ours=cluster.proposal_number))
        if (proposal_number > cluster.proposal_number) and (not(cluster.voted)  and not(cluster.leaderx)):
            try:
                print("Seems we have not voted before\n\n")
                cluster.voted = {"proposal_number": proposal_number, "voted": member_id}
                return response_ack
            except:
                return None

        # If the cluster has better leader information
        elif cluster.voted:
            if proposal_number > cluster.voted['proposal_number']:
                try:
                    print("A better proposal {proposal} than voted {v} from {idx}\n\n".format(proposal=proposal_number, v=cluster.voted['proposal_number'], idx=member_id))
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
                    print("A better proposal {proposal} than in leaderx {lx} from {idx}\n\n".format(proposal=proposal_number, lx=cluster.leaderx['proposal_number'], idx=member_id))
                    cluster.voted = {"proposal_number": proposal_number, "voted": member_id}
                    return response_ack
                except:
                    return None
            else:
                return response_nack

        else:
            return response_nack

 

    async def leader(self):
        print('\nLeader Role')
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
                # Only request for votes from other members
                if member["cluster_id"] != self.member_id:
                    try:
                        task = asyncio.create_task(make_post_request(member["cluster_id"], payload_ack, RESPONSETIMEOUT))
                        tasks.append(task)
                    except asyncio.TimeoutError:
                        print(f"Timeout Error: {member['cluster_id']}")
                        break
                else:
                    print("I am the leader, no Acks I know")
            responses_ack = await asyncio.gather(*tasks)

        print("As leader we need to send heartbeat messages")

        try:
            self.leadership_timer = None
            tx = await self.start_heartbeat()


        except Exception as e:
            print(f"Error: {e}")

        #print("Do we get here, let us sleep for 5sec")
        #time.sleep(5)


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

        with open('/tmp/eval_da.txt', 'a') as fp:
            fp.write("ackVote: {leader} with proposal {proposal} at {ts}\n".format(leader=cluster.leaderx["leader"], proposal=cluster.leaderx["proposal_number"], ts=datetime.datetime.now().strftime("%M:%S.%f")[:-2]))

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

        print("The leader {leader} with proposal {proposal} is Alive - reset timer".format(leader=leader_id, proposal=proposal_number))

        cluster.leaderx = {"proposal_number": proposal_number, "leader": leader_id}

        with open('/tmp/eval_da.txt', 'a') as fpi:
            fpi.write("informMember: {leader} with proposal {proposal} at {ts}\n".format(leader=leader_id, proposal=proposal_number, ts=datetime.datetime.now().strftime("%M:%S.%f")[:-2]))

        cluster.reset_leadership_timer()

        #if leader_id != cluster.member_id:
        #    print("I am strictly a member")

        #
        #    cluster.state = 'member'

        return Success(None)

    @method
    def pollLeader() -> Result:
        # Candidate can always poll the leader 
        return None
 

async def make_post_request(peer_id, payload, timeout):
    # Send the message to the specified peer
    url = "http://"+peer_id
    headers = {'content-type': 'application/json'}

    print(f"Request to {url} made at {time.monotonic()}")

    async with aiohttp.ClientSession() as session:
        start_time = time.monotonic()
        try:
            print(f"Sending post request to {url}")
            resp = await asyncio.wait_for(session.post(url, data=json.dumps(payload), headers=headers), timeout=RESPONSETIMEOUT)

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



# JSON-RPC routes
@app.route('/', methods=['POST'])
def index():
    req = request.get_data().decode()
    response = dispatch(req)
    return Response(str(response), status=200, mimetype='application/json')


if __name__ == '__main__':

    # This retrieves members of the distributed system [Can be provided to any of the roles]
    ##members = retrieve_clusters_info()

    members = [{'name': 'amd156', 'ip_address': '128.110.219.67', 'port': 5002, 'cluster_id': '128.110.219.67:5002'},
           {'name': 'amd015', 'ip_address': '128.110.218.254', 'port': 5002, 'cluster_id': '128.110.218.254:5002'},
           {'name': 'hp017', 'ip_address': '128.110.218.56', 'port': 5002, 'cluster_id': '128.110.218.56:5002'},
           {'name': 'hp034', 'ip_address': '128.110.218.73', 'port': 5002, 'cluster_id': '128.110.218.73:5002'},
           {'name': 'amd002', 'ip_address': '128.110.218.241', 'port': 5002, 'cluster_id': '128.110.218.241:5002'}]

    member_id = ip_address + ':' + str(port)

    cluster = Cluster(member_id, 'member', members)
    print("Successfully created the cluster object ")

    # Create a logger for the cluster thread
    cluster_logger = logging.getLogger('cluster')
    cluster_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    cluster_logger.addHandler(handler)

    # Configure Flask's own logging
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    print("Starting the cluster thread")
    cluster_thread = threading.Thread(target=cluster.run)
    cluster_thread.daemon = True
    cluster_thread.start()


    print("Starting LE Service on {ip_address}:{port}".format(ip_address=ip_address, port=port))
    app.run(debug=False, host = ip_address, port=port)