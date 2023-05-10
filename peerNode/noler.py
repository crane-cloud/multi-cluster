import random
import threading
import time
from jsonrpcserver import Success, method, serve, InvalidParams, Result, Error
from util import retrieve_clusters_info
from timer import BaseTimer

REQUESTVOTETIMER = 25
RESPONSEVOTETIMER = 35
LEADERSHIPVOTETIMER = 50
LEADERSHIPTERMTIMER = 600
POLLLEADERTIMER = 100

class Cluster:
    # The initial state of a cluster member (the member may eventually take on the roles of voter, leader or candidate)
    def __init__(self, member_id, members):
        self.member_id = member_id # unique identifier of the member (address & port)
        self.members = members # cluster info as per the view {A dictionary of the cluster members}
        self.state = 'member' # initial state of member
        self.votes = {{}} # the votes a member receives in election rounds
        self.leader = {} # the current leader information at this cluster
        self.proposal_number = 0 # the initial proposal number
        self.leader_size = len(members) // 2 + 1 # quorum size to guarantee leadership

    # We perform a set of functions based on the state of the cluster
    def run(self):
        while True:
            if self.state == 'member':
                self.member()
            elif self.state == 'voter':
                self.voter()
            elif self.state == 'leader':
                self.leader()
            elif self.candidate == 'candidate':
                self.candidate()

    def member(self):
        self.proposal_number += 1
        #vote_counter = 0
        for member in self.members:
            #Compute the profile of each member & send as part of the request
            #Example profile of a voter
            pf_voter = 4.5

            #Set the requestVoteTimer

            try:
                serv_conn = Server("http://"+host+":"+str(port))
                if serv_conn:
                    resp = serv_conn.requestVote(self.member_id, self.proposal_number, profile_voter)
                    
                    #Check if there is a responseVote() message from the member
                    if resp["status"] == 200:
                        self.votes = {self.proposal_number: {voter_id}}
            except:
                return None          
        
        # We set the responseVoteTimer - we expect the results from all the peers
        # We count the votes at this point (For the latest proposal number, we count the votes)
        # Example: self.votes = {1: {peer1, peer2, peer3}}
        ## - len(self.votes[1] = 3)
        if len(self.votes[proposal_number]) > self.leader_size:
            #We can now execute the leader role functions - send ackVote
            self.state = 'leader'
            
        else:
            print('We back off for a random bounded time: 10ms - 100ms')
            time.sleep(randint(10,100)/1000)

            # We expect another node (especially the candidates) to start LE
            if not (self.leader):
                print('We start a new election cycle with a new proposal number')
                
                # We may need to pull out the requestVote function - to be easily called?
                # It would be easy to repeat here with just a new proposal number:
                self.proposal_number += 1


    def voter(self):
        self.voter_id = member_id
        
        # this will be computed or determined later (static for now)
        profile_member = 6.5

        # At the start, voted and leader entries are empty
        self.voted = {}
        self.leader = {}

        # If never voted or received a leader result, check the profile  (if better, respond)
        if not(self.voted)  and not(self.leader):
            if profile_member > profile_voter:
                try:
                    serv_conn = Server("http://"+host+":"+str(port))
                    if serv_conn:
                        responseVote(self.member_id, self.proposal_number, profile_voter)
                except:
                    return None
                # Update the voted map with P#, profile & id of member voted
                self.voted = {proposal_number, member_id, profile_member}
            else:
                self.state = 'candidate'
        
        # If the cluster voted, confirm this is a fresh election
        if self.voted or self.leader:
            # No further checks: a voter must have accepted leader information with better/fresh proposals'
            if proposal_number > self.voted['proposal_number'] or proposal_number > self.leader['proposal_number']:
                if profile_member > profile_voter:
                    try:
                        serv_conn = Server("http://"+host+":"+str(port))
                        if serv_conn:
                            serv_conn.responseVote(self.member_id, self.proposal_number, profile_voter)
                    except:
                        return None
                    self.voted = {proposal_number: {member_id, profile_member}}
                else:
                    self.state = 'candidate'

            else:
                return None


    def leader(self):
        self.leader_id = member_id
        #As a leader, send ackVote & informMember messages to all the members

        for member in self.members:
            try:
                serv_conn = Server("http://"+member['cluster_id']+":"+str(port))
                if serv_conn:
                    serv_conn.ackVote(self.leader_id, self.proposal_number)
            except:
                return None

        # Run the timer & keep informing members about leadership


    def candidate(self):
        #We arrive here as a result of one of the profiles better than some proposal profile
        self.candidate_id = candidate_id

        #We set the LeadershipVoteTimer [We expect a leader within this time]
        #If this expires, and there is no ackVote message - we begin an election phase

        # If within this period, we receive an ackVote and subsequent leader update - we revert to the member role

        # Or we remain with this role, and keep polling the leader to ensure it is live - increased chances of taking over
    
    #-----------------------------#
    # The following are jsonrpcserver RPC methods (@method) that a peer can invoke
    @method
    def requestVote(member_id, proposal_number, profile_voter) -> Result:
        #At the receipt of requestVote, the member state is changed to voter
        self.state = 'voter'

        #A responseVote message is returned to the vote initiating member
        return responseVote()

    
    @method
    def responseVote(member_id, voter_id, proposal_number):
        #Message sent to a member as a vote
        return None


    @method
    def ackVote(member_id, proposal_number):
        #A voter or member receives the ackVote message as confirmation of winner (leader)
        self.leader = [member_id, proposal_number]
        #return None

    @method
    def informMember(proposal_number, leader_id):
        #If a member receives this message (should be from the leader), the leaderShipTermTimer is reset
        return None

    @method
    def pollLeader() -> Result:
        # Candidate can always poll the leader 
        return None

    if __name__ == '__main__':
        # This retrieves members of the distributed system [Can be provided to any of the roles]
        members = retrieve_clusters_info()
        