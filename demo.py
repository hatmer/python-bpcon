"""
Reads and maintains config file
Creates an object with an update() function to pass to BPCon
Starts BPCon instance 
Demonstrates API functions

"""

import asyncio
import websockets
import sys
import hashlib
import time

from BPCon.protocol import BPConProtocol
from configManager import ConfigManager, log
from BPCon.utils import shell
from state import StateManager

if len(sys.argv) == 2:
    configFile = sys.argv[1]
else:
    configFile = "config.ini"

class BPConDemo:
    def __init__(self):
        try:
            self.startup() 
            self.state = StateManager(self.conf)
            self.loop = asyncio.get_event_loop()
            self.bpcon = BPConProtocol(self.conf, self.state)
            self.paxos_server = websockets.serve(self.bpcon.main_loop, self.conf['ip_addr'], self.conf['port'], ssl=self.conf['ssl'])
            self.loop.run_until_complete(self.paxos_server)
            log.info("Started BPCon on port {}".format(self.conf['port']))

            if self.conf['is_client']:
                log.debug("is client. making test requests")
                for x in range(1):
                    self.commit("P,{},hello{}".format(x,x))
                    self.commit("P,test,value")
                    self.commit("P,test{},value{}".format(x,x))
                    self.commit("P,test2,value2")
                    self.commit("P,test,value3")
                    self.commit("D,test2,")

                log.debug("requests complete")     

        except Exception as e:
            log.info(e)

    def commit(self,msg):
        self.loop.run_until_complete(self.bpcon_request(msg))

    def got_commit_result(self, future):
        if future.done():
            if not future.cancelled():
                self.log.info("commit result: {}".format(future.result()))
            else:
                self.log.info("future cancelled")
        else:
            self.log.info("future not done")

    @asyncio.coroutine
    def bpcon_request(self, msg):
        log.debug("making request: {}".format(msg))
        bpcon_task = asyncio.Future()
        bpcon_task.add_done_callback(self.got_commit_result)
        try:
            timer_result = asyncio.wait_for(bpcon_task, 3.0) # timer possibly unneccessary
            commit_result = yield from self.bpcon.request(msg, bpcon_task) # returns boolean
            log.info("bpcon request result: {}".format(commit_result))
            return commit_result

        except asyncio.TimeoutError:
            log.info("bpcon commit timed out")
        except asyncio.CancelledError:
            log.info("bpcon commit future cancelled")
        except Exception as e:
            log.debug(e)        

    def startup(self):
        """
        startup routine
        Loads from cloned state

        """
        # clean working dir and extract config, creds, and state
        log.info("Cleaning working directory...")
        command = "rm config.ini && rm -rf data && rm -rf creds"
        shell(command)
        log.info("Extracting cloned state...")
        command = "tar xzf clone.tar.gz"
        shell(command)
        # load config
        log.info("Loading configuration...")
        self.cm = ConfigManager()
        self.conf = self.cm.load_config(configFile)


        # load state
        log.info("Loading state...")
        self.state = StateManager(self.conf)
        self.state.load_state()

    """
    def clone(self):
        
        #create a copy of db, peers, peer creds, and config
        #save to compressed archive
        #used to add new nodes to system
        
        try:
            self.state.image_state()
            self.cm.save_config()
            backupdir = "data/"
            cfile = "config.ini"
            command = "tar czf clone.tar.gz {} {} creds/".format(cfile,backupdir)
            shell(command)
            log.info("clone of state successfully created")

        except Exception as e:
            log.info("clone of state failed")

    def handle_reconfig_request(self, epoch=0):
        toreturn = self.bpcon.bmsgs
        if epoch != 0:
            self.clone()
            with open('clone.tar.gz', 'r') as fh:
                toreturn += "<>{}".format(fh.read())
                log.debug("cloned state added successfully")

        return toreturn    

    def make_reconfig_request(self, wss):
        # epoch = current epoch
        pass
    """

    def shutdown(self):
        print("\nShutdown initiated...")
        print("\nDatabase contents:\n{}".format(self.bpcon.state.db.kvstore)) # save state here
        self.paxos_server.close()
    

def start():
    if len(sys.argv) > 2:
        print("Usage: python demo.py <configfile>")
    else:    
        try:
            c = BPConDemo()
            try:
                try:
                    asyncio.get_event_loop().run_forever()
                except Exception as e:
                    log.info("mainloop exception")
                    log.error(e)
            except KeyboardInterrupt:
                c.shutdown()
            finally:
                asyncio.get_event_loop().close()
                print('\nShutdown complete')
        except Exception as e:
            log.info("System failure: {}".format(e))
start()

