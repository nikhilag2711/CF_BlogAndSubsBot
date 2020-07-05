import datetime

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
