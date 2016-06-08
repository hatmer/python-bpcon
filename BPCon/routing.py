import hashlib
import os
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from BPCon.utils import save_state, load_state
from collections import OrderedDict

class GroupManager(object):
    """
    This class manages peers for BPCon

    stores secure websockets keyed to IP address 
    
    manages peer pubkeys and certificates
    
    """
    def __init__(self, conf):
        self.conf = conf
        self.keyspace = (0.0,0.0)
        self.peers = OrderedDict() # group members
        self.num_peers = 0

    def init_local_group(self):    
        self.keyspace = (0.0,1.0)

        # add self
        with open(self.conf['keyfile'], 'r') as fh:
            key = fh.read()
        with open(self.conf['certfile'], 'r') as fh:
            cert = fh.read()

        self.add_peer(self.conf['p_wss'], key + "<>" + cert)

        for wss in self.conf['peerlist']:
            fname = self.conf['peer_keys'] + self.get_ID(wss)+".pubkey"
            if os.path.isfile(fname):
                #read key and add pair to self.peers
                with open(fname, 'r') as fh:
                    self.peers[wss] = RSA.importKey(fh.read()) 
            else:
                self.conf['log'].info("missing key file for {}".format(wss))
        
        self.num_peers = len(self.peers)

    def quorum_size(self):
        return int((self.num_peers / 2) + (self.num_peers % 2))

    def get_ID(self, sock_str):
        encoded =  hashlib.sha1(sock_str.encode())
        return encoded.hexdigest()

    def add_peer(self, sock_str, creds):
        try:
            key,cert = creds.split('<>')
            #sock_str = "wss://"+str(ip)+":"+str(port)
            ID = self.get_ID(sock_str)
            if not sock_str in self.peers.keys():
                key = str(key)
                self.peers[sock_str] = RSA.importKey(key) 
                self.conf['log'].debug("add peer: key imported")
                # write key to file
                with open(self.conf['peer_keys']+ID+".pubkey", 'w') as fh:
                    fh.write(key)
                with open("{}{}.crt".format(self.conf['peer_certs'],ID), 'w') as fh:
                    fh.write(cert)
                self.num_peers += 1
                return True
        except Exception as e:
            self.conf['log'].debug(e)
        return False    

    def remove_peer(self, wss):
        if self.peers[wss]:
            self.peers.pop(wss, None)
            self.num_peers -= 1
            return True
        else:
            self.conf['log'].debug("remove failed")
            return False

    def get_all(self):
        # returns list of addresses of peers in group
        sockets = list(self.peers.keys())
        sockets.remove(self.conf['p_wss']) # don't want to send to self
        return sockets

        
    def verify_sigs(self, msglist):
        num_verified = 0
        
        for item in msglist:
            wss, msg, sig = item.split(';')
            if wss in self.peers:
                
                rsakey = self.peers[wss]
                h = SHA.new(msg.encode())

                sigmsg = int(sig).to_bytes(256, byteorder='little')
                verifier = PKCS1_v1_5.new(rsakey)
                if verifier.verify(h, sigmsg):
                    num_verified += 1
            else:        
                self.conf['log'].info("missing a key for {}".format(wss))

        return num_verified

    def save(self,gid):
        fname = "data/bpcon_routing_{}.pkl".format(gid)
        tosave = [self.peers, self.keyspace]
        save_state(fname,tosave)
    
    def load(self,gid):
        (self.peers, self.keyspace) = load_state('data/bpcon_routing_{}.pkl'.format(gid))

