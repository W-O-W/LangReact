from langreact.core.common.event import Event
def test_event():
    a1 = Event(id="A",description="a")
    a2 = Event(id="A",description="a")
    assert a1 == a2

def test_event_set():
    s = set([
        Event(id="A",description="a"),
        Event(id="B",description="b")
    ])

    c1 = Event(id="A",description="a")
    assert c1 in s

    c2 = Event(id="A",description="a")
    assert c2 in s

    c3 = Event(id="C",description="a")
    assert c3 not in s

    c4 = Event(id="B",description="b")
    assert c4 in s