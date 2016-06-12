from BPCon.routing import GroupManager
from BPCon.storage import InMemoryStorage
from Crypto.Hash import SHA
import pickle
import time

class StateManager:
    def __init__(self, conf): # init_state=None):
        self.log = conf['log']
        
        self.db = InMemoryStorage()

    def update(self, val, ballot_num=-1):
        self.log.debug("updating state: ballot #{}, op: {}".format(ballot_num, val))
        if not ',' in val:
            # requires unpackaging
            length, data = val.split('<>')
            val = int(data).to_bytes(int(length), byteorder='little').decode()

        t,k,v = val.split(',')
        
        #DB requests
        if t == 'P':
            self.db.put(k,v)
        elif t == 'D':
            self.db.delete(k)
    
    def image_state(self):
        # create disc copy of system state 
        try:
            # These saved to data directory
            self.db.save()
        except Exception as e:
            self.log.debug("save state failed: {}".format(e))

    def load_state(self):
        try:
            self.db.load()
        except Exception as e:
            self.log.debug("load state failed: {}".format(e))
