from ..dispatcher import Dispatcher

def test_empty():
    d = Dispatcher()
    assert len(d) == 0
