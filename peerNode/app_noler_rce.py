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
from profile_controller.controller import profile_controller
import functools
import json
from collections import deque
from util import retrieve_clusters_info
import copy

ELECTIONTIMEOUT = 2.7 #seconds
RESPONSETIMEOUT = 2.1 #seconds, used outside class
POSTREQUESTTIMEOUT = 2.1 #seconds

#Fast path timeouts
FASTPATH_ELECTIONTIMEOUT = 0.60 #seconds

app = Flask(__name__)

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
port = int(os.getenv("LE_PORT", 5002))

cached_data_queue = deque(maxlen=10)

class Cluster:
    # The initial state of a cluster member (the member may eventually take on the roles of voter, leader or candidate)
    def __init__(self, member_id, state, members):
        self.member_id = member_id # unique identifier of the member (address & port)
        self.members = members # cluster info as per the view {A dictionary of the cluster members}
        self.state = state # initial state of member
        self.proposal_number = 0 # the initial proposal number
        self.voted = {} # who this member has voted
        self.leaderx = {} # the leader information at this member

        self.leadership_timeout = 2.4 #seconds [period after which a member can claim leadership | leader unresponsive]
        self.leadership_timer = None # [timer for leadership timeout - member | candidate]
        self.heartbeat_interval = 1.5 #seconds [leader sends heartbeat to followers]

        # Candidate state timer variables
        self.leadership_vote_timer = None # [timer for leadership vote timeout - candidate]
        self.leadership_vote_timeout = 1.3 #seconds [period after which a candidate can claim leadership]

        self.pollleader_timer = None # [timer for poll leader timeout - alive]
        self.pollleader_timeout = 1.8 #seconds [period after which a candidate can claim leadership]
        self.pollleader_interval = 1.2 #seconds [period after which a candidate can poll leader]

        # Election cycle timeouts
        self.election_timeout = ELECTIONTIMEOUT #seconds [period for completion of an election cycle]
        self.response_timeout = RESPONSETIMEOUT #seconds [period after which a member expects a response from other each member]
        self.post_request_timeout = POSTREQUESTTIMEOUT #seconds [period after which a member expects a response from any post request]

        # Normal Path
        self.noler_timeout = 5.0 #seconds [period after which NoLeR has failed]
        self.noler_timer = None # [timer for NoLeR timeout - member | candidate]


    # We perform a set of functions based on the state of the cluster
    def run(self):
        print('Run Mode with thread {thread}'.format(thread=threading.current_thread().name))
        self.reset_noler_timer()
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


    # Reset timer functions #

    # A function to reset the leadership timer
    def reset_leadership_timer(self):
        print("Resetting the leadership timer - received informMember")
        if self.leadership_timer:
            self.leadership_timer.cancel()
        self.leadership_timer = threading.Timer(self.leadership_timeout, lambda: None)
        self.leadership_timer.start()

    # A function to reset the leadership vote timer
    def reset_leadership_vote_timer(self):
        print("Resetting the leadership vote timer - candidate")
        if self.leadership_vote_timer:
            self.leadership_vote_timer.cancel()
        self.leadership_vote_timer = threading.Timer(self.leadership_vote_timeout, lambda: None)
        self.leadership_vote_timer.start()

    # A function to reset the poll leader timer
    def reset_pollleader_timer(self):
        print("Resetting the poll leader timer - alive")
        if self.pollleader_timer:
            self.pollleader_timer.cancel()
        self.pollleader_timer = threading.Timer(self.pollleader_timeout, lambda: None)
        self.pollleader_timer.start()     

    # A function to reset the NoLeR timer
    def reset_noler_timer(self):
        print("Resetting the NoLeR timer - member | candidate")
        if self.noler_timer:
            self.noler_timer.cancel()
        self.noler_timer = threading.Timer(self.noler_timeout, lambda: None)
        self.noler_timer.start()

    async def async_op(self, payload):
        print("An async Op")
        async with aiohttp.ClientSession() as session:
            tasks = []
            for member in self.members:

                # Only request for votes from other members
                if member["cluster_id"] != self.member_id:
                    profilex = get_profile_by_cluster_id(member["cluster_id"])
                    print("Profile for member {member}: {profilex}".format(member=member["cluster_id"], profilex=profilex))

                    payload_update = copy.deepcopy(payload)

                    payload_update["params"]["profile"] = profilex
                    print("Payload Election: {payload_update}".format(payload_update=payload_update))

                    try:
                        task = asyncio.create_task(make_post_request(member["cluster_id"], payload_update, self.post_request_timeout))
                        tasks.append(task)
                    except asyncio.TimeoutError:
                        print(f"Timeout Error: {member['cluster_id']}")
                        continue
                else:
                    continue
            responses = await asyncio.gather(*tasks)

        print("Printing response from post request in async_op")
        print(responses)

        return responses


    async def start_election_cycle(self):
        
        print("Proposal 00: {proposal}".format(proposal=self.proposal_number))
        self.proposal_number += 1
        print("Proposal 01: {proposal}".format(proposal=self.proposal_number))
        self.votes = {self.proposal_number: []}
        leader_size = len(self.members) // 2  #node votes itself by default, hence +1

        print("A new election cycle started with proposal {proposal} at time {ts}".format(proposal=self.proposal_number, ts=time.time()))

        with open('/tmp/eval_da.txt', 'a') as fps:
                fps.write("Election: {member} with proposal {proposal} at {ts}\n".format(member=self.member_id, proposal=self.proposal_number, ts=datetime.datetime.now().strftime("%M:%S.%f")[:-2]))


        payload_request_votes = {
            "method": "requestVote",
            "params": {
                "self": None,
                "member_id": self.member_id,
                "proposal_number": self.proposal_number,
                "profile": None
                },
            "jsonrpc": "2.0",
            "id": 1,
            }

        try:
            responses = await asyncio.wait_for(self.async_op(payload_request_votes), timeout=self.response_timeout)
        except asyncio.TimeoutError as e:
            print(f"Timeout Error in [start_election_cycle]: {e}")
            return None

        if responses:
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

            try:

                print("Number of votes received: {votes}".format(votes=len(self.votes[self.proposal_number])))

                if len(self.votes[self.proposal_number]) >= leader_size:
                #We can now execute the leader role functions - send ackVote

                    with open('/tmp/eval_da.txt', 'a') as fpx:
                        fpx.write("Leader: {leader} with proposal {proposal} at {ts}\n".format(leader=self.member_id, proposal=self.proposal_number, ts=datetime.datetime.now().strftime("%M:%S.%f")[:-2]))

                    self.state = 'leader'
                else:
                    print("Unsuccessful election cycle - role revert")

                    if self.state == 'candidate':
                        self.state = 'candidate'
                    
                    if self.state == 'member':
                        self.state = 'member'

                    return None

            except Exception as e:
                print(f"Exception in vote count: {e}")

                if self.state == 'candidate':
                    self.state = 'candidate'
                    
                if self.state == 'member':
                        self.state = 'member'

                return None

        else:

            print("Unsuccessful election cycle - role revert")

            if self.state == 'candidate':
                self.state = 'candidate'
                    
            elif self.state == 'member':
                self.state = 'member'

            return None


    async def member(self):

        print('\n\n\nMember Role with proposal number: {proposal} at time {ts}'.format(proposal=self.proposal_number, ts=time.time()))
        print("Thread name:", threading.current_thread().name)

        if self.leaderx or cluster.leaderx:

            print("I have a leader with ID {idx} at proposal {proposal}".format(idx = self.leaderx["leader"], proposal = self.leaderx["proposal_number"]))

        else:
            with open('/tmp/eval_da.txt', 'a') as fpm:
                fpm.write("noLeader: {member} with proposal {proposal} at {ts}\n".format(member=self.member_id, proposal=self.proposal_number, ts=datetime.datetime.now().strftime("%M:%S.%f")[:-2]))

        # Check if first instance/run
        if self.leadership_timer is None:
            # We start a new election cycle
            print("No leaderx, so we start a new election cycle")

            # possibly a new election on hence timeout
            try:
                await asyncio.wait_for(self.start_election_cycle(), timeout=self.election_timeout) # within the largest latency range

            except asyncio.TimeoutError as e:
                print(f"Timeout Error in [member]: {e}")
                
        elif self.leadership_timer and self.leadership_timer.is_alive():
            print("Leadership timer set to expire in", self.leadership_timer.interval, "seconds")

        else:
            print("Leadership timer has already expired - leader dead?")
            with open('/tmp/eval_da.txt', 'a') as fpx:
                fpx.write("Expired: {leader} with proposal {proposal} at {ts}\n".format(leader = self.leaderx["leader"], proposal = self.leaderx["proposal_number"], ts=datetime.datetime.now().strftime("%M:%S.%f")[:-2]))

            await asyncio.wait_for(self.start_election_cycle(), timeout=self.election_timeout)
        # We can wait here...

        time.sleep(self.heartbeat_interval)


    async def start_heartbeat(self):
        print("In the start_heartbeat")
        payload_inf = {
            "method": "informMember",
            "params": {
                "self": None,
                "leader_id": self.member_id,
                "proposal_number": self.proposal_number,
                "profile": None
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
                        # Only send request to other members
                        if member["cluster_id"] != self.member_id:
                            try:
                                profilei = get_profile_by_cluster_id(member["cluster_id"])
                                print("Profile for member {member}: {profile}".format(member=member["cluster_id"], profile=profilei))
                                payload_inf["params"]["profile"] = profilei
                                print("Payload at informMember: {payload}".format(payload=payload_inf))
                                task = asyncio.create_task(make_post_request(member["cluster_id"], payload_inf, self.post_request_timeout))
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


    async def start_pollleader(self):
        print("In the start_pollleader of the candidate")
        self.proposal_number = self.leaderx["proposal_number"]
        self.reset_pollleader_timer()
        self.reset_noler_timer()

        payload_pl = {
            "method": "pollLeader",
            "params": {
                "self": None,
                "candidate_id": self.member_id,
                },
            "jsonrpc": "2.0",
            "id": 3,
            }

        while True:

            if self.state == 'candidate' and self.leaderx:
                #todo
                #leader_prc = get_profile_by_cluster_id(member_id=self.leaderx["leader"])

                print("\n\nPolling leader {leader} with {payload}".format(leader=self.leaderx["leader"], payload=payload_pl))

                try:
                    response = await make_post_request(self.leaderx["leader"], payload_pl, self.post_request_timeout)

                    if response is not None:
                        print("Leader Alive at Candidate poll: Response {response} received".format(response=response))
                        self.reset_pollleader_timer() # no special need
                        self.reset_noler_timer()
                    else:
                        print("Leader Dead at Candidate - Now start a new election cycle")

                        with open('/tmp/eval_da.txt', 'a') as fppd:
                            fppd.write("Dead: Leader {leader} with proposal {proposal} at {ts}\n".format(leader = self.leaderx["leader"], proposal = self.leaderx["proposal_number"], ts=datetime.datetime.now().strftime("%M:%S.%f")[:-2]))

                        await asyncio.wait_for(self.start_election_cycle(), timeout=self.election_timeout)

                            ### Maybe we shouldn't for another election
                            #if response["result"]["params"][1] >= leader_p:
                            #    print("Leader profile is worse, start election cycle")
                            #    with open('/tmp/eval_da.txt', 'a') as fppc:
                            #        fppc.write("lowProfile: {leader} with proposal {proposal} at {ts}\n".format(leader = self.leaderx["leader"], proposal = self.leaderx["proposal_number"], ts=datetime.datetime.now().strftime("%M:%S.%f")[:-2]))

                            #    self.proposal_number = self.leaderx["proposal_number"]
                            #    await asyncio.wait_for(self.start_election_cycle(), timeout=self.election_timeout)
 
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    print(f"Timeout|Connect Error for leader: {self.leaderx['leader']}, dead?")

                    with open('/tmp/eval_da.txt', 'a') as fppd:
                        fppd.write("Dead? Error: Leader {leader} with proposal {proposal} at {ts}\n".format(leader = self.leaderx["leader"], proposal = self.leaderx["proposal_number"], ts=datetime.datetime.now().strftime("%M:%S.%f")[:-2]))
                    await asyncio.wait_for(self.start_election_cycle(), timeout=self.election_timeout)           

                # We sleep for the poll leader interval & then send another poll
                print("Sleeping for {interval} seconds".format(interval=self.pollleader_timeout))
                time.sleep(self.pollleader_timeout)
                #time.sleep(self.compute_backoff() / 1000.0)

            else:
                print("Not a candidate and/or have no leader\n\n")
                break


    def voter(self, member_id, profilev, proposal_number):

        print('\n\nVoter Method')

        voter_id = cluster.member_id

        print("Received vote request from {member} with proposal {proposal} and MY profile {profilev}".format(member=member_id, proposal=proposal_number, profilev=profilev))

        response_ack = {
            "response": "responseVote",
            "params": [voter_id, proposal_number],
        }

        # Fixes a bug on the dispatcher method of jsonrpcserver
        response_nack = {
            "response": "noVote",
            "params": [voter_id, proposal_number],
        }

        member_profile = get_profile_by_cluster_id(member_id)

        print("Vote request: Member profile {idx1}:{profile1} & My profile {idx2}:{profile2}".format(profile1=member_profile, profile2=profilev,idx1=member_id,idx2=cluster.member_id))

        # If never voted or received a leader result
        print("Vote proposal numbers, request: {req} and mine: {ours}".format(req=proposal_number, ours=cluster.proposal_number))
        if (proposal_number > cluster.proposal_number) and (not(cluster.voted)  and not(cluster.leaderx)):
            try:
                print("Seems we have not voted before\n\n")

                if cluster.noler_timer and cluster.noler_timer.is_alive():
                    print("NoLeR timer set to expire in", cluster.noler_timer.interval, "seconds") 

                    if profilev > member_profile:
                        print("My profile {idx1}:{profile1} > Member profile {idx2}:{profile2}".format(profile1=profilev, profile2=member_profile,idx1=cluster.member_id,idx2=member_id))

                        if cluster.state == 'member':

                            print("Changing state to candidate...")
                            #start the leadership_vote_timer
                            cluster.reset_leadership_vote_timer()
                            cluster.state = 'candidate'

                        return response_nack
                
                    else:
                        print("My profile {idx1}:{profile1} <= profile {idx2}:{profile2}".format(profile1=profilev, profile2=member_profile,idx1=cluster.member_id,idx2=member_id))
                        cluster.voted = {"proposal_number": proposal_number, "voted": member_id, "profile": member_profile}
                        return response_ack

                else:
                    print("Normal Path Election - NoLeR timer expired")
                    cluster.voted = {"proposal_number": proposal_number, "voted": member_id, "profile": member_profile}
                    return response_ack


            except Exception as e:
                print("Exception in voter method: {e}".format(e=e))
                return None

        # If the cluster has better voted information
        elif cluster.voted:
            print("We have voted before\n\n")

            print("Proposal numbers:- Member: {member}:{member_p}, Ours: {cluster}:{cluster_p}, and Voted {voted}:{voted_p}".format(member=member_id, member_p=proposal_number, 
            cluster=cluster.member_id,cluster_p=cluster.proposal_number, voted=cluster.voted['voted'], voted_p=cluster.voted['proposal_number']))

            try:
                if (proposal_number > cluster.proposal_number) and (proposal_number > cluster.voted['proposal_number']):

                    if cluster.noler_timer and cluster.noler_timer.is_alive():
                        print("NoLeR timer set to expire in", cluster.noler_timer.interval, "seconds")

                        if (member_profile >= profilev):
                            print("Our profile is bad - in voted")

                            if (member_profile >= cluster.voted['profile']): # if better than the voted, we ACK immediately
                                print("Voted: New Member Profile {idx1}:{profile1} is >= Voted Profile {idx2}:{profile2}".format(profile1=member_profile,profile2=cluster.voted['profile'],idx1=member_id, idx2=cluster.voted['voted']))
                                cluster.voted = {"proposal_number": proposal_number, "voted": member_id, "profile": member_profile}
                                return response_ack

                            else:
                                print("Voted: New Member Profile {idx1}:{profile1} is < Voted Profile {idx2}:{profile2}".format(profile1=member_profile,profile2=cluster.voted['profile'],idx1=member_id, idx2=cluster.voted['voted']))
                                return response_nack

                        else:
                            print("Voted: New Member Profile {idx1}:{profile1} is < Our Profile {idx2}:{profile2}".format(profile1=member_profile,profile2=profilev, idx1=member_id, idx2=cluster.member_id))
                          
                            if cluster.state == 'member':
                                print("Changing state to candidate.....") # only if we are not a candidate or leader
                                cluster.reset_leadership_vote_timer()
                                cluster.state = 'candidate'
                            return response_nack

                    else:
                        print("Normal Path Election in Voted - NoLeR timer expired")
                        cluster.voted = {"proposal_number": proposal_number, "voted": member_id, "profile": member_profile}
                        return response_ack

                else:
                    print("Stale election - in voted\n\n")
                    return response_nack

            except Exception as e:
                print("Exception in voter.voted method: {e}".format(e=e))
                return None

        # If the cluster has leader information, confirm this is a fresh election & profiles are good
        elif cluster.leaderx:
            #print("Received leader {leader} info before with better proposal {proposal} than {l}".format(leader=cluster.leaderx['leader'], proposal=cluster.leaderx['proposal_number'], l=proposal_number))
            print("We have received leader info\n\n")

            print("Proposal numbers:- Member: {member}:{member_p}, Ours: {cluster}:{cluster_p}, and Voted {leader}:{leader_pr}".format(member=member_id, member_p=proposal_number, cluster=cluster.member_id,cluster_p=cluster.proposal_number, leader=cluster.leaderx['leader'], leader_pr=cluster.leaderx['proposal_number']))

            try:

                if (proposal_number > cluster.proposal_number) and (proposal_number > cluster.leaderx['proposal_number']):

                    if cluster.noler_timer and cluster.noler_timer.is_alive():
                        print("NoLeR timer set to expire in", cluster.noler_timer.interval, "seconds")

                        if (member_profile >= profilev):

                            print("Our profile is bad - in leaderx")
                  
                            if (member_profile >= cluster.leaderx['profile']):
                                print("Leaderx: New Member Profile {idx1}:{profile1} is >= Leader Profile {idx2}:{profile2}".format(profile1=member_profile,profile2=cluster.leaderx['profile'],idx1=member_id, idx2=cluster.leaderx['leader']))
                                cluster.voted = {"proposal_number": proposal_number, "voted": member_id, "profile": member_profile}
                                return response_ack

                            else:
                                print("Leaderx: New Member Profile {idx1}:{profile1} is < Leader Profile {idx2}:{profile2}".format(profile1=member_profile,profile2=cluster.leaderx['profile'],idx1=member_id, idx2=cluster.leaderx['leader']))
                                return response_nack
                        else:
                            print("Leaderx: New Member Profile {idx1}:{profile1} is < Our Profile {idx2}:{profile2}".format(profile1=member_profile,profile2=profilev, idx1=member_id, idx2=cluster.member_id))
 
                            if cluster.state == "member":
                                print("Changing state to candidate.....") # only if not leader
                                cluster.reset_leadership_vote_timer()
                                cluster.state = 'candidate'
                        
                            return response_nack

                    else:
                        print("Normal Path Election in Leaderx - NoLeR timer expired")
                        cluster.voted = {"proposal_number": proposal_number, "voted": member_id, "profile": member_profile}
                        return response_ack

                else:
                    print("Stale election - in leaderx\n\n")
                    return response_nack

            except Exception as e:
                    print("Exception in voter method: {e}".format(e=e))
                    return None
        else:
            print("None of the above - I am a potential leader")
            return response_nack


    async def leader(self):
        print('\nLeader Role')
        #As a leader, send ackVote message to all the members

        self.leaderx = {"leader": self.member_id, "proposal_number": self.proposal_number, "profile": 1}
        self.voted = {"proposal_number": self.proposal_number, "voted": self.member_id, "profile": 1}

        print("As leader, this is my ID: {idx} and proposal number: {proposal}".format(idx=self.member_id, proposal=self.proposal_number))

        payload_ack = {
            "method": "ackVote",
            "params":{
                "self": None,
                "member_id": self.member_id,
                "proposal_number": self.proposal_number,
                "profile": None
                },
            "jsonrpc": "2.0",
            "id": 4,
            }

        print(payload_ack)

        async with aiohttp.ClientSession() as session:
            tasks = []
            for member in self.members:
                # Only request for votes from other members
                if member["cluster_id"] != self.member_id:
                    try:
                        profilea = get_profile_by_cluster_id(member["cluster_id"])
                        print("Profile for member {member}: {profile}".format(member=member["cluster_id"], profile=profilea))
                        payload_ack["params"]["profile"] = profilea
                        print("Payload at ackVote: {payload}".format(payload=payload_ack))
                        task = asyncio.create_task(make_post_request(member["cluster_id"], payload_ack, self.post_request_timeout))
                        tasks.append(task)
                    except asyncio.TimeoutError:
                        print(f"Timeout Error: {member['cluster_id']}")
                        break
                else:
                    print("I am the leader, no Acks from/for me")
            responses_ack = await asyncio.gather(*tasks)

        print("As leader we need to send heartbeat messages")

        try:
            self.leadership_timer = None
            tx = await self.start_heartbeat()

        except Exception as e:
            print(f"Error: {e}")


    async def candidate(self):
        print('Candidate Role.....')
        #We arrive here as a result of one of the profiles better than some proposal profile

        #We set the LeadershipVoteTimer [We expect a leader within this time]
        #If this expires, and there is no ackVote message - we begin an election phase

        if not self.leaderx:
            if self.leadership_vote_timer and self.leadership_vote_timer.is_alive():
                print("Leadership vote timer set to expire in", self.leadership_vote_timer.interval, "seconds")
            else:
                print("Leadership vote timer has already expired - starting candidate election cycle")
                with open('/tmp/eval_da.txt', 'a') as fpcx:
                    fpcx.write("Fast Path: New candidate {candidate} with proposal {proposal} at {ts}\n".format(candidate=self.member_id, proposal = self.proposal_number, ts=datetime.datetime.now().strftime("%M:%S.%f")[:-2]))

                await asyncio.wait_for(self.start_election_cycle(), timeout=self.election_timeout) # fast path

        else:
            print("We have a leader, so we just poll it")
            if cluster.state != 'leader' and cluster.state != 'member':
                tl = await self.start_pollleader()


    # Compute the backoff time for the next election cycle
    def compute_backoff(self):
        
        profile_o = 0

        for member in self.members:
            if member["cluster_id"] != self.member_id:
                profile_o += get_profile_by_cluster_id(member["cluster_id"])
            
        profile_o = (profile_o / (len(self.members) - 1)) * 300

        #print(profile_o)
        print("The backoff time is: {backoff} ms".format(backoff=profile_o))

        return profile_o


    #-----------------------------#
    # The following are jsonrpcserver RPC methods (@method) that a peer can invoke
    @method
    def requestVote(self, member_id, profile, proposal_number) -> Result:
        #At the receipt of requestVote, the member state is changed to voter

        print("requestVote request from member: {member} with proposal: {proposal}".format(member=member_id, proposal=proposal_number))

        result = Cluster.voter(self, member_id, profile, proposal_number)

        if result:
            print("Now providing a responseVote or noVote to client")
            print(result)
            return Success(result)
        else:
            print("Voter method returned None")
            return None

    @method
    def ackVote(self, member_id, proposal_number, profile):
        #A voter or member receives the ackVote message as confirmation of winner (leader)

        leader_profile = get_profile_by_cluster_id(member_id)


        print("Cluster state at ackVote: {ack}".format(ack=cluster.state))
        cluster.leaderx = {"proposal_number": proposal_number, "leader": member_id, "profile": leader_profile}

        with open('/tmp/eval_da.txt', 'a') as fp:
            fp.write("ackVote: {leader} with proposal {proposal} at {ts}\n".format(leader=cluster.leaderx["leader"], proposal=cluster.leaderx["proposal_number"], ts=datetime.datetime.now().strftime("%M:%S.%f")[:-2]))

        #For future elections, we update our proposal number
        cluster.proposal_number = proposal_number # this can interfere with a current election cycle

        print("Updated my proposal number to: {proposal}".format(proposal=cluster.leaderx["proposal_number"]))

        print("I have a new leader {leader} (voted or not) with proposal {proposal} and MY profile {profile}!".format(leader=cluster.leaderx["leader"], proposal=cluster.leaderx["proposal_number"], profile=cluster.leaderx["profile"]))

        response = {
            "response": "ackEd",
            "params": [cluster.leaderx["leader"], cluster.leaderx["proposal_number"], cluster.leaderx["profile"]],
        }

        #Not a very useful response as it is not required - we could write another post for these kind of messages

        # Only change the state of the member not leader or candidate

        if (member_id != cluster.member_id) and (cluster.state != "candidate") and (cluster.state != "leader"):
            cluster.reset_noler_timer()
            cluster.reset_leadership_timer()
            cluster.state = "member"

        if cluster.state == "candidate":
            cluster.reset_noler_timer()
            cluster.reset_pollleader_timer()
            

        return Success(response)

    @method
    def responseVote(message):
        #Message sent to a member as a vote
        return None


    @method
    def informMember(self, leader_id, profile, proposal_number):
        #If a member receives this message (should be from the leader), the leaderShipTermTimer is reset

        leader_profile = get_profile_by_cluster_id(leader_id)

        print("Received the informMember message from leader {leader} with proposal {proposal} and MY profile {profile}".format(leader=leader_id, proposal=proposal_number, profile=profile))
        print("The leader {leader} with proposal {proposal} is alive: ITS profile {profile1} - MY profile {profile2}".format(leader=leader_id, proposal=proposal_number, profile1=leader_profile, profile2=profile))

        cluster.leaderx = {"proposal_number": proposal_number, "leader": leader_id, "profile": leader_profile}

        #Update the proposal number for future elections
        cluster.proposal_number = proposal_number
        

        with open('/tmp/eval_da.txt', 'a') as fpi:
            fpi.write("informMember: {leader} with proposal {proposal} at {ts}\n".format(leader=leader_id, proposal=proposal_number, ts=datetime.datetime.now().strftime("%M:%S.%f")[:-2]))

        #Check for significant profile changes /coming
        #leader_profile = get_profile_by_cluster_id(leader_id)
        #profile_theta = profile - candidate_profile # Check for significant profile changes /coming
        #if profile_theta > 0:

        #if profile > leader_profile:
        #    cluster.proposal_number = cluster.leaderx["proposal_number"]
        #    #await asyncio.wait_for(cluster.start_election_cycle(), timeout=cluster.election_timeout)

        #else:

        #if cluster.state != "candidate" or cluster.state != "leader":
        #cluster.state = "member"

        if (leader_id != cluster.member_id) and (cluster.state != "candidate") and (cluster.state != "leader"):
            cluster.reset_noler_timer()
            cluster.reset_leadership_timer()
            cluster.state = "member"

        if cluster.state == "candidate":
            cluster.reset_noler_timer()
            cluster.reset_pollleader_timer()

        return Success(None)

    @method
    def pollLeader(self, candidate_id) -> Result:
        # Candidate can always poll the leader

        print("Received the pollLeader message from Candidate {candidate}".format(candidate=candidate_id))

        ##if proposal_number == cluster.proposal_number:
        candidate_profile = get_profile_by_cluster_id(candidate_id)

        print("In the PL at leader, candidate profile is {candidate}:{profile}".format(candidate=candidate_id, profile=candidate_profile))

            #profile_theta = profile - candidate_profile # Check for significant profile changes /coming

        return Success({"response": "polledLeader", "params": [cluster.member_id, candidate_profile]})
        ##else:   
            
        ##    return Success(None)


async def make_post_request(peer_id, payload, timeout):
    # Send the message to the specified peer
    url = "http://"+peer_id.replace(":5001", ":5002")
    headers = {'content-type': 'application/json'}

    print(f"Request to {url} made at {time.monotonic()}")

    async with aiohttp.ClientSession() as session:
        start_time = time.monotonic()
        try:
            print(f"Sending post request to {url}")
            resp = await asyncio.wait_for(session.post(url, data=json.dumps(payload), headers=headers), timeout=RESPONSETIMEOUT) # timeout value outside class

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
        except aiohttp.ClientError as ceerror:
            print(f"Client error for server {url}: {ceerror}")
            return None
        except aiohttp.client_exceptions.ClientConnectorError as ccerror:
            print(f"Connection error for server {url}: {ccerror}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None


#Get profile of the member given the member_id
def get_profile_by_cluster_id(member_id):
    cluster_object = find_member_data(member_id)
    
    if cluster_object is None:
        return None
    return cluster_object['profile']

#Functions to update and retrieve the cache data
@functools.lru_cache(maxsize=None)
def cached_data():
    print("Retriving new data points:")
    data = profile_controller()
    cached_data_queue.append(json.dumps(data))
    return cached_data_queue[-1] 

def get_cached_data():
    if not cached_data_queue:
        cached_data()
    return json.loads(cached_data_queue[-1])

def run_cached_data():
    while True:
        cached_data()
        #for member in members:
        #    print("Peer {peer}: Profile: {profile}".format(peer = member['cluster_id'], profile = get_profile_by_cluster_id(member['cluster_id'])))

        #print("\nSleeping for 15 seconds")
        time.sleep(15)

def find_member_data(target_id):
    cached_data = get_cached_data()
    for item in cached_data:
        if item['target'].split(':')[0] == target_id.split(':')[0]:
            name = item['target']
            cluster_id = item['target']
            ip_address, port = item['target'].split(':')
  
            new_object = {
                'name': name,
                'ip_address': ip_address,
                'port': int(port),
                'cluster_id': cluster_id,
                'profile': item['profile']
            }
            return new_object

    return None

# JSON-RPC routes
@app.route('/', methods=['POST'])
def index():
    req = request.get_data().decode()
    response = dispatch(req)
    return Response(str(response), status=200, mimetype='application/json')


if __name__ == '__main__':

    # This retrieves members of the distributed system [Can be provided to any of the roles]
    members = retrieve_clusters_info()

    member_id = ip_address + ':5001'

    cluster = Cluster(member_id, 'member', members)
    print("Successfully created the cluster object ")

    # Create a logger for the cluster thread
    cluster_logger = logging.getLogger('cluster')
    cluster_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    cluster_logger.addHandler(handler)

    # Create a logger for the profile thread
    profile_logger = logging.getLogger('profile')
    profile_logger.setLevel(logging.INFO)
    handlerp = logging.StreamHandler()
    handlerp.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    profile_logger.addHandler(handlerp)

    # Configure Flask's own logging
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    print("Starting the cluster thread")
    cluster_thread = threading.Thread(target=cluster.run)
    cluster_thread.daemon = True
    cluster_thread.start()

    print("Starting the profile thread")
    profile_thread = threading.Thread(target=run_cached_data)
    profile_thread.daemon = True
    profile_thread.start()

    print("Starting LE Service on {ip_address}:{port}".format(ip_address=ip_address, port=port))
    app.run(debug=False, host = ip_address, port=port)