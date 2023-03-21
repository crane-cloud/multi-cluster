import random
import threading
from util import retrieve_clusters_info

class Node:
    def __init__(self, member_id, members):
        self.member_id = member_id
        self.members = members
        self.state = 'member'
        self.proposal_number = 0
        self.leader_size = len(members) // 2 + 1


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

    def voter(self):
        self.voter_id = voter_id

    def leader(self):
        self.leader_id = leader_id

    def candidate(self):
        self.candidate_id = candidate_id

    def requestVote():
        return None


    if __name__ == '__main__':
        members = retrieve_clusters_info()
        