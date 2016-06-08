import random

class Quorum(object):
    """
    manages ballots

    """
    def __init__(self, ballot_num, num_peers):
        self.N = ballot_num
        self.num_peers = num_peers
        self.quorum = int(num_peers / 2) #+ (num_peers % 2))
        self.acceptors = 0
        self.rejectors = 0
        self.peer_msgs = {} 
        self.commits = 0
        self.current_ballots = {} # list of seen maxBallots from peers

    def add_1b(self, mb, msg, peer_wss):
        if peer_wss not in self.peer_msgs.keys():
            self.peer_msgs[peer_wss] = msg
            if mb < self.N:
                self.acceptors += 1
            else:
                self.rejectors += 1
                # keep track of maxBallots seen
                if mb in self.current_ballots:
                    self.current_ballots[mb] += 1
                else:
                    self.current_ballots[mb] = 1
                
    def rejecting_quorum_member(self):
        if max(self.current_ballots.values()) >= self.quorum:
            return random.choice(self.peer_msgs.keys()) # random wss from quorum that has seen a higher ballot

    def add_2b(self, N):
        if N == self.N:
            self.commits += 1

    def quorum_2b(self):
        return self.commits >= self.quorum

    def quorum_1b(self):
        # returns True if majority vote achieved
        return ((self.acceptors >= self.quorum) or (self.rejectors >= self.quorum))

    def got_majority_accept(self):
        # returns True for accepted, False for rejected
        return self.acceptors >= self.rejectors
    
    def get_msgs(self):
        return ",".join(k+";"+v for (k,v) in self.peer_msgs.items())

