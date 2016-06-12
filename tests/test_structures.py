from BPCon import storage, routing, quorum

def test_storage():
    s = storage.InMemoryStorage()
    s.put("abc", "555")
    assert s.get("abc") == "555"

    
def test_routing():
    r = routing.RoutingManager()
    r.add_peer("127.0.0.1", 8000, "123", "456")
    assert list(r.get_all()) == ['wss://127.0.0.1:8000']
    assert r.num_peers == 1
    assert r.get("127.0.0.1") == 'wss://127.0.0.1:8000'
    r.remove_peer("127.0.0.1")
    assert r.num_peers == 0

def test_quorum():
    q = quorum.Quorum(1, 5)
    q.add(1, 0, "q", "w")
    q.add(1, 0, "e", "r")
    assert q.is_quorum() == False
    q.add(1, 0, "t", "y")
    assert q.is_quorum() == True

    assert q.get_signatures() == 'w,r,y'
