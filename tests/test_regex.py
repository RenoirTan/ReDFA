from redfa.regex import compile as re_compile


def test_regex_0():
    regex = re_compile("(a|b)*a")
    
    assert regex.find("a") == (0, 1)
    assert regex.find("b") is None
    assert regex.find("aa") == (0, 2)
    assert regex.find("ca") == (1, 2)


def test_regex_1():
    regex = re_compile("(a+b*)*a(a|b)")
    
    assert regex.find("aabab") == (0, 5)
    assert regex.find("c") is None
    assert regex.find("baab") == (1, 4)
    assert regex.find("acb") is None


def test_regex_2():
    regex = re_compile("a?b")
    
    assert regex.find("aaaa") is None
    assert regex.find("baa") == (0, 1)
    assert regex.find("aaab") == (2, 4)
    assert regex.find("bab") == (0, 1)


def test_regex_3():
    regex = re_compile("(11)*(00|10)*")
    
    assert regex.find("") == (0, 0)
    assert regex.find("111111") == (0, 6)
    assert regex.find("1100") == (0, 4)
    assert regex.find("01010") == (0, 0)