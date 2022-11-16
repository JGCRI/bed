# content of test_sample.py
def inc(x):
    return x + 1

def sum(x,y):
    return x + y


def test_inc():
    assert inc(3) == 5

def test_sum():
    assert sum(3,4) == 5