Python-BPCon
============

Byzantine Paxos as specified by Lamport in [*Byzantizing Paxos by Refinement*](http://research.microsoft.com/en-us/um/people/lamport/tla/byzsimple.pdf).

Byzantine Paxos is a more resilient version of the Paxos algorithm. To “Byzantine” an algorithm means to modify it such that the system that uses it is resilient to malicious nodes. BPCon is the byzantined version of PCon, a reduced form of Paxos derived via a computer-verified proof system.

<h2>Requirements</h2>

python3.4, asyncio, websockets, pycrypto

<h2>Usage</h2>

```python
python3 demo.py
```


