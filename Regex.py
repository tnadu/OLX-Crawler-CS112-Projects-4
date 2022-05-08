import re

title = ''
description = ''

def singleRoom(title, description):
    regex=re.compile(r'(garsonier[aăe]|studio)', re.IGNORECASE)
    if regex.search(title) or regex.search(description):
        return True
    return False

def yearOfConstruction(title, description):
    regex=re.compile(r'an(ul)?\s*(20[12]\d|19\d{2})', re.IGNORECASE)
    number = re.compile('\d+')

    if regex.search(title):
        return int(number.search(regex.search(title).group()).group())
    elif re.search(regex, description):
        return int(number.search(regex.search(description).group()).group())

    return False

def rental(title, description):
    regex=re.compile(r'([iî]n)?\s*chiri(e|ez|at|[aă]m|ere)', re.IGNORECASE)
    if regex.search(title) or regex.search(description):
        return True
    return False