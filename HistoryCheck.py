##Change these variables as needed
TotalNeededCommentKarma = 300
FakeKarmaThreshhold = 100
NumRecentPostThreshhold = 15
##--

import traceback
import Remover

def HistoryKarmaCheck(User, UserComments, KarmaSubs, RequestOrComment, PostID, VisibleKarma=0, FakeKarma=0, TotalKarma=None):
    try:
        for comment in UserComments:
            if comment is None:
                break
            else:
                VisibleKarma = VisibleKarma + comment.score
                ##Below is search for comments from subs for Free karma; variable as at top of file for easy access
                if str(comment.subreddit) in KarmaSubs and str(comment.subreddit) != 'arma':
    ##                print(KarmaSubs, comment.score)    ##Debug line to track fake karma obtained from a specific post
                    
                    ##Below updates how much karma Requester has gotten from Karma subs
                    FakeKarma = FakeKarma + comment.score
                    TotalKarma = comment.author.comment_karma - FakeKarma
    ##                print("REQUEST", comment.author, "has", TotalKarma, "after subtracting", FakeKarma, 'Fake Karma after adding', comment.score, "from", comment.subreddit)  ##Debug line to ensure karma from comments is being tracked accurately
        KarmaText = str(str(User) + ' has ' + str(TotalKarma) + " valid karma, " + str(FakeKarma) + " fake karma;")
        if TotalKarma is not None and TotalKarma < TotalNeededCommentKarma: ##If Requester has enough adjusted karma per sub rules; variable at top of file for ease of access        
            RemovalReason="Karma"
            print(KarmaText, "removing")
            Remover.GeneralRemove(RequestOrComment, PostID, RemovalReason)
            
    ##    elif TotalKarma is not None and FakeKarma > FakeKarmaThreshhold:  ##Checks if X karma from karma subs counted in their top 1000 comments; variable at tope of file for ease of access
    ##        print(KarmaText, "removing as karma threshhold met")
    ##        Remover.GeneralRemove(RequestOrComment, PostID, RemovalReason)
            
        elif TotalKarma is not None:
    ##        print(KarmaText, "approving", RequestOrComment)    ##Debug line if they're on the cusp of being denied but are ultimately allowed
            pass
        else:   ##If no fake karma detected
    ##        print(KarmaText, "approving", RequestOrComment)  ##Debug line to make sure it's just people not breaking rules as opposed to the bot not working
            pass
            
            
    except Exception as e:
        print("HistoryKarmaCheck", e, traceback.format_exc())


def HistoryGiveawayCheck(User, UserGiveawayHistory, GiveawaySubs, RequestOrComment, PostID, GiveawaySubCount=0, TotalSubCount=0):
    try:
        import time
        import re
        RemovalReason = "GiveawayUsage"
        for post in UserGiveawayHistory:
            if post is None:
                break
            ThreeMonths = 86400*90 #86400 seconds is 1 day
            TimeDifference = int(time.time())-int(post.created_utc)
            if TimeDifference > ThreeMonths:
                break
            if post.banned_by!=None:
                continue
            TotalSubCount = TotalSubCount + 1
    ##        print(post.author, post.subreddit)    ##Debug line to track it's reading subreddits from user history
            if str(post.subreddit) not in GiveawaySubs:
                continue
            GiveawaySub = str(post.subreddit)
            if "discussion" in post.permalink:
                continue
            if "intro" in post.permalink:
                continue
            if "announcement" in post.permalink:
                continue
            if "gog" in post.permalink and "request" not in post.permalink and "offer" not in post.permalink:
                continue
            if "meta" in post.permalink and "Steam_Giveaway" in str(post.subreddit).lower():
                continue
##            print(post.author, post.subreddit, post.id, GiveawaySubCount)   ##Debug line to track which post is being checked and total count
            if hasattr(post, '_submission'): #This checks COMMENTS even though it is unintuitive
                if post.is_submitter == True: #Skips comments on own post
                    continue
                if "request" in str(post.permalink).lower():
                    continue
                global CommentBody
                CommentBody = post.body
                RootComment = post.is_root
                if RootComment is False:
                    continue
                if "not entering" in CommentBody or "not participating" in CommentBody or "not taking part" in CommentBody:
    ##                print("User not participating - skipping", post.author, GiveawaySubCount)   ##Debug line to track comments being omitted from GiveawaySubCount
                    continue
            else: #Checks requests
                if post.removed_by_category != None: #if submission removed, un-count it
                    TotalSubCount = TotalSubCount - 1
                RootComment = True
            GiveawaySubCount = GiveawaySubCount + 1
                
        GiveawaySubText = str(str(User) + " has " + str(GiveawaySubCount) + " giveaway posts out of " + str(TotalSubCount))
        if TotalSubCount < NumRecentPostThreshhold:
    ##        print(GiveawaySubText, "- approving", RequestOrComment) ##Debug line to check num of giveaway subs and total subs
            pass
        elif GiveawaySubCount > (TotalSubCount/2):
            print(GiveawaySubText, "- removed", RequestOrComment)
            RemovalReason = "GiveawayUsage"
            Remover.GeneralRemove(RequestOrComment, PostID, RemovalReason)
            pass
        else:
    ##        print(GiveawaySubText, "- approving", RequestOrComment) ##Debug line to check num of giveaway subs and total subs
            pass
            
    except Exception as e:
        print("HistoryGiveawayCheck", e, traceback.format_exc())
