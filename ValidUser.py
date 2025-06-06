import praw
from prawcore.exceptions import NotFound
import traceback

def ValidUserCheck(reddit, User):
    try:
        reddit.redditor(User).id
        return 1
    except NotFound as e:
        # print(User, "not found", e)
        return 0
    except AttributeError as e:
        # print(User, "is lacking an id; likely suspended")
        return 3
    except Exception as e:
        print(e, traceback.format_exc())
        return 2
    
        
