import re

title = ''
description = ''


def isHouse(title, description):
    regex = re.compile('vil[aă]|cas[aă]|duplex|house', re.IGNORECASE)
    if regex.search(title) or regex.search(description):
        return True
    return False


def isForExchange(title, description):
    regex = re.compile('schimb|troc', re.IGNORECASE)
    if regex.search(title) or regex.search(description):
        return True
    return False
