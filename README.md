Python-BPCon
============

Byzantine Paxos as specified by Lamport in [*Byzantizing Paxos by Refinement*](http://research.microsoft.com/en-us/um/people/lamport/tla/byzsimple.pdf).

<h2>Protocol Description</h2>

Byzantine Paxos is a more resilient version of the Paxos algorithm. To “Byzantine” an algorithm means to modify it such that the system that uses it is resilient to malicious nodes. BPCon is the byzantined version of PCon, a reduced form of Paxos derived via a computer-verified proof system.

Python-BPCon is an implementation of the BPCon protocol that functions as an API for replicated key-value storage. It replicates updates to a database object to all the servers in the system.

Lamport describes multiple ways for the BPCon system to verify messages in order to prevent malicious nodes from disrupting the protocol. The protocol specification below uses RSA signatures appended to the 1b messages to prevent malicious nodes from falsifying quorum acceptance.

The protocol for BPCon is as follows:

Input: an update to the database in string format
Output: a notification of replication success/failure

System Variables 
```python
maxBal = -1 # highest ballot seen 
maxVBal = -1 # highest ballot voted in 
maxVVal = None # value voted for 
maxVBal avs = {} # msg dict keyed by value 
bmsgs = [] # log of messages sent by this instance 
```

Message Formats 
```html
1aMsg: N 
1bMsg: N, maxVBal, maxVVal, avMsg, sig 
1cMsg: N, proposal, sigList 
avMsg: maxVBal, maxVVal 
2bMsg: N, proposal 
bmsgs: 1aMsg U 1bMsg U 1cMsg U avMsg U 2bMsg
```

A node with a proposal for the system submits a 1a request to all its peers. 
```html
bmsgs := bmsgs U ("1a", bal) 
```

The peers receive the 1a message and respond with a signed 1b message.
```html
bmsgs := bmsgs U ("1b", bal, acceptor, avs, maxVBal, maxVVal) 
```

The proposing node receives 1b messages from its peers. If a quorum, i.e. at least half of its peers, responds with 1b maxVBal greater than the proposing node's maxVBal, then this node becomes aware that it is out-of-sync with the group and performs a resyncronization routine. If a quorum sent a 1b response with a maxVBal less than the proposal's ballot number, then the proposing node submits a 1c message with the proposed value for this round and the list of signed 1b messages. The other nodes verify the signatures for each 1b message in order to ensure that a quorum of nodes did in fact accept the proposal.

Each peer verifies the 1c message. It commits the proposed update and sends a 2b response if it is able to confirm the validity of the signed 1b messages. If the proposing node receives 2b messages from a quorum of peers it knows that its proposal was accepted.


<h2>Requirements</h2>

python3.4, asyncio, websockets, pycrypto
