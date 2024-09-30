User = 'whybeingparanoid'
KarmaOrGiveaway = 'Giveaway'

import traceback
import time
import re
import praw

reddit = praw.Reddit('GOGUserHistoryBot', user_agent='GOGUserHistoryBot_2')
GoG = reddit.subreddit("GiftofGames")
TotalNeededCommentKarma = 300
FakeKarmaThreshhold = 100
NumRecentPostThreshhold = 15
PostHistory = 250
UserGiveawayHistory = reddit.redditor("{}".format(User)).new(limit=PostHistory)    ##Returns set amount of activity from User
UserComments = reddit.redditor("{}".format(User)).comments.top(limit=None) ##Returns top 1000 comments from User
KarmaSubs = "FreeKarma|FreeKarma4U|FreeKarma4You|DeFreeKarma|FreeKarmaSub4Sub|FreeKarama4UandMe|FreeKarma4NUDES|FreeKarmaForU|FreeKarma247|freekarmafromme|karmawhore|KarmaStore|FreeKarmaSubreddit|FreeKarmaChooChoo|GetFreeKarmaAnyTime|upvote|KarmaForFree|FreeKarma4All|Karma_Exchange|karma4karma|getkarma|MoreFreeKarma4U"
GiveawaySubs = "GiftofGames|Free|RandomActs|RandomActsOfGaming|RandomActsofKindess|randomactsofcsgo|RandomActsOfChristmas|Giveaway|Random_Acts_Of_Amazon|randomactsofamazon|RandomActsOfPolish|playitforward|steam_giveaway|RandomActsOfTf2|LeagueOfGiving|Random_Acts_of_Etsy|Random_Acts_of_Lush|RandomKindess|Random_Acts_Of_Pizza"
VisibleKarma=0 
FakeKarma=0 
TotalKarma=None
GiveawaySubCount=0
TotalSubCount=0

if KarmaOrGiveaway == 'Karma':
    try:
        for comment in UserComments:
            if comment is None:
                break
            else:
                VisibleKarma = VisibleKarma + comment.score
                ##Below is search for comments from subs for Free karma; variable as at top of file for easy access
                if str(comment.subreddit) in KarmaSubs:
                    print(KarmaSubs, comment.score)    ##Debug line to track fake karma obtained from a specific post
                    
                    ##Below updates how much karma Requester has gotten from Karma subs
                    FakeKarma = FakeKarma + comment.score
                    TotalKarma = comment.author.comment_karma - FakeKarma
                    print("REQUEST", comment.author, "has", TotalKarma, "after subtracting", FakeKarma, 'Fake Karma after adding', comment.score, "from", comment.subreddit)  ##Debug line to ensure karma from comments is being tracked accurately
        KarmaText = str(str(User) + ' has ' + str(TotalKarma) + " valid karma, " + str(FakeKarma) + " fake karma;")
        if TotalKarma is not None and TotalKarma < TotalNeededCommentKarma: ##If Requester has enough adjusted karma per sub rules; variable at top of file for ease of access        
            RemovalReason="Karma"
            print(KarmaText, "removing")
            
    ##    elif TotalKarma is not None and FakeKarma > FakeKarmaThreshhold:  ##Checks if X karma from karma subs counted in their top 1000 comments; variable at tope of file for ease of access
    ##        print(KarmaText, "removing as karma threshhold met")
    ##        Remover.GeneralRemove(RequestOrComment, PostID, RemovalReason)
            
        elif TotalKarma is not None:
            print(KarmaText, "approved")    ##Debug line if they're on the cusp of being denied but are ultimately allowed
            pass
        else:   ##If no fake karma detected
            print(KarmaText, "approved")  ##Debug line to make sure it's just people not breaking rules as opposed to the bot not working
            pass
            
            
    except Exception as e:
        print("HistoryKarmaCheck", e, traceback.format_exc())


if KarmaOrGiveaway == 'Giveaway':
    try:
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
            print(post.author, post.subreddit)    ##Debug line to track it's reading subreddits from user history
            GiveawaySub = re.search(rf'(?i)^({GiveawaySubs})$', str(post.subreddit))
            if GiveawaySub is not None and "discussion" not in post.permalink and "intro" not in post.permalink and "announcement" not in post.permalink and "gog" not in post.permalink:
                if "meta" in post.permalink and "Steam_Giveaway" in str(post.subreddit).lower():
                    continue
                GOGThread = re.search(rf'(?i)(?<!offer_gog)(?<!offergog)GOG', post.permalink)
                if GOGThread is not None:
                    continue
                print(post.author, post.subreddit, post.id, GiveawaySubCount)   ##Debug line to track which post is being checked and total count
                if hasattr(post, '_submission'): #This checks COMMENTS even though it is unintuitive
                    if post.is_submitter == True: #skip comments on own post
                        continue
                    RequestReply = re.search(rf'(?i)REQUEST', post.permalink)
                    if RequestReply is not None:
                        continue
                    global CommentBody
                    CommentBody = post.body
                    RootComment = post.is_root
                    if RootComment is False:
                        print("User is replying - skipping", post.author, GiveawaySubCount)   ##Debug line to track comments being omitted from GiveawaySubCount
                        continue
                    if ("not entering" or "not participating" or "not taking part") in (CommentBody):
                        print("User not participating - skipping", post.author, GiveawaySubCount)   ##Debug line to track comments being omitted from GiveawaySubCount
                        continue
                else: #Checks requests
                    if post.removed_by_category != None: #if submission removed, un-count it
                        TotalSubCount = TotalSubCount - 1
                    RootComment = True
                GiveawaySubCount = GiveawaySubCount + 1
                
        GiveawaySubText = str(str(User) + " has " + str(GiveawaySubCount) + " giveaway posts out of " + str(TotalSubCount))
        if TotalSubCount < NumRecentPostThreshhold:
            print(GiveawaySubText, "- approved for low # of posts") ##Debug line to check num of giveaway subs and total subs
            pass
        elif GiveawaySubCount > (TotalSubCount/2):
            print(GiveawaySubText, "- removed")
            RemovalReason = "GiveawayUsage"
            pass
        else:
            print(GiveawaySubText, "- approved") ##Debug line to check num of giveaway subs and total subs
            pass
            
    except Exception as e:
        print("HistoryGiveawayCheck", e, traceback.format_exc())
