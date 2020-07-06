import datetime, json, requests

def isValidInteger(s):
    try:
        int(s)
    except ValueError:
        return False
    num = int(s)
    return num

def isValidDate(s) :
    if len(s) == 4:
        try:
            datetime.datetime.strptime(s, '%Y')
        except ValueError:
            return False
        date = datetime.datetime.strptime(s, '%Y')
        return date
    elif len(s) == 6:
        try:
            datetime.datetime.strptime(s, '%m%Y')
        except ValueError:
            return False
        date = datetime.datetime.strptime(s, '%m%Y')
        return date
    elif len(s) == 8:
        try:
            datetime.datetime.strptime(s, '%d%m%Y')
        except ValueError:
            return False
        date = datetime.datetime.strptime(s, '%d%m%Y')
        return date
    else :
        return False

def tag_match(tags, latest_blog) :
    for tag in latest_blog['tags']:
        for chk in tags:
            if tag.find(chk) != -1:
                return latest_blog
    return False

def check(official, virtual, practice, unoff, part):
    if part == 'CONTESTANT' and official :
        return 1
    if part == 'VIRTUAL' and virtual :
        return 1
    if part == 'PRACTICE' and practice :
        return 1
    if part == 'OUT_OF_COMPETITION' and unoff :
        return 1
    return 0

def check_status(ac, official, virtual, practice, unoff, verdict, part):
    if not official and not virtual and not practice and not unoff :
        if ac:
            if verdict == 'OK':
                return 1
        else:
            if verdict == 'OK':
                return 1
            else:
                return 2
    else:
        if ac:
            if verdict == 'OK':
                return check(official, virtual, practice, unoff, part)
        else:
            if verdict == 'OK':
                return check(official, virtual, practice, unoff, part)
            else:
                return check(official, virtual, practice, unoff, part) + 1
    return 0
