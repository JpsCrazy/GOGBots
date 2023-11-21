#!/use/bin/python
import praw
import time
import datetime
import traceback
#import mysql.connector

from prawcore.exceptions import NotFound

##local files
import Deletions
import CooldownRemover
import GiftLog
import HistoryCheck
import Modmail
import SteamBot
import ReceiversGamingPlatform
import Remover
import RequestLimiter
import UserFlair
import ValidUser
import WikiWrite

##database link because we aren't cavemen
#mydb = mysql.connector.connect(
  #host="localhost",
  #user="bots",
  #password="bots",
  #database="bots",
  #port=8458,
  #buffered=True
#)
#dbcursor = mydb.cursor()

ModList = "AutoModerator", "DjSoulFuck", "Saadieman", "freedomtacos", "Miniboyss", "Jaska95", "OurRobotOverlord", "JpsCrazy", "JpsCrazysBot", "fallen_fire", "MarioDesigns", "rollovertherainbow", "darkducote"
KarmaSubs = "FreeKarma|FreeKarma4U|FreeKarma4You|DeFreeKarma|FreeKarmaSub4Sub|FreeKarama4UandMe|FreeKarma4NUDES|FreeKarmaForU|FreeKarma247|freekarmafromme|karmawhore|KarmaStore|FreeKarmaSubreddit|FreeKarmaChooChoo|GetFreeKarmaAnyTime|upvote|KarmaForFree|FreeKarma4All|Karma_Exchange|karma4karma|getkarma|MoreFreeKarma4U"
GiveawaySubs = "GiftofGames|Free|RandomActs|RandomActsOfGaming|RandomActsofKindess|randomactsofcsgo|RandomActsOfChristmas|Giveaway|Random_Acts_Of_Amazon|randomactsofamazon|RandomActsOfPolish|playitforward|steam_giveaway|RandomActsOfTf2|LeagueOfGiving|Random_Acts_of_Etsy|Random_Acts_of_Lush|RandomKindess|Random_Acts_Of_Pizza"
##r/Giveaways not included because it doesn't seem to be the same as the others
##Above subs should be formatted "SUBREDDIT|SUBREDDIT|SUBREDDIT|etc"

##Below variables probably don't need to be changed ever
PostHistory = 250

##Need file in same directory named "praw.ini" with the below text filled out
##[Default]
##oauth_url=https://oauth.reddit.com
##reddit_url=https://www.reddit.com
##short_url=https://redd.it

##[GOGUserHistoryBot]
##client_id=YOUR_CLIENT_ID_API
##client_secret=YOUR_CLIENT_SECRET_API
##password=YOUR_REDDIT_PASSWORD
##username=YOUR_REDDIT_USERNAME
##user_agent=GOGUserHistoryBot_2.0

reddit = praw.Reddit('GOGUserHistoryBot', user_agent='GOGUserHistoryBot_2')
GoG = reddit.subreddit("GiftofGames")
GoGdeletes = reddit.subreddit("GoGdeletes")

##--------------------------------------------------------------------
##--------------------------------------------------------------------
##-----------------START OF ACTUAL PROGRAM----------------------------
##--------------------------------------------------------------------
##--------------------------------------------------------------------

print("User Reddit History bot starting...")
        
while True:
    
    Deletions.DeletionChecker(reddit, GoG, GoGdeletes)
    CooldownRemover.CooldownRemover(reddit, GoG)
    Modmail.ModMailCheck(reddit, ModList)
    try:
        print(datetime.datetime.now(), 'Starting Request check...')
        for submission in GoG.stream.submissions(pause_after=-1):
            if submission is None:
                time.sleep(60)
                break

            if submission.banned_by!=None:
                continue

            if submission.removed is True:
                continue

            RequestOrComment = "Request"
            User = submission.author
            Title = submission.title
            BodyText = submission.selftext
            PostID = submission.id
            SubmissionDate = submission.created_utc
            Delay = time.time() - SubmissionDate
            
            if User=="OurRobotOverlord":
                continue

            if Delay < 90:
                continue

            PostLogLine = "https://reddit.com/comments/" + str(PostID) + "/" + str(User)
            if PostLogLine in GoG.wiki["postlog"].content_md:
                continue
            WikiWrite.WriteWiki("postlog", PostLogLine, GoG)
            
            if "[request]" in str(Title).lower():
                try:
                    ThreeDays = 86400*3 #86400 seconds is 1 day
                    TimeDifference = int(time.time())-int(SubmissionDate)
                    if TimeDifference < ThreeDays:
#                             print('Starting RequestLimiter.RepostCheck()')
                        RequestLimiter.RepostCheck(reddit, User, SubmissionDate, PostID)
                    
#                         print('Starting RequestLimiter.PCTagCheck()')
                    RequestLimiter.PCTagCheck(User, Title, PostID, GoG)
                    
#                         print('Starting ReceiversGamingPlatform.ProfileChecker()')
                    ReceiversGamingPlatform.ProfileChecker(User, BodyText, RequestOrComment, PostID, GoG)

#                         print('Starting HistoryCheck.HistoryKarmaCheck()')
                    UserComments = reddit.redditor("{}".format(submission.author)).comments.top(limit=None) ##Returns top 1000 comments from User
                    HistoryCheck.HistoryKarmaCheck(User, UserComments, KarmaSubs, RequestOrComment, PostID)
                    
#                         print('Starting HistoryCheck.HistoryGiveawayCheck()')
                    UserGiveawayHistory = reddit.redditor("{}".format(submission.author)).new(limit=PostHistory)    ##Returns set amount of activity from User
                    HistoryCheck.HistoryGiveawayCheck(User, UserGiveawayHistory, GiveawaySubs, RequestOrComment, PostID)
                    
                except Exception as e:
                    print(datetime.datetime.now(), "Requests", e, traceback.format_exc())

            ###--Puts users on cooldown if multiple [GOG] posts within past month
            elif "[gog]" in str(Title).lower() and "[offer]" not in str(Title).lower() and "[request]" not in str(Title).lower() and "[discussion]" not in str(Title).lower() and "[intro]" not in str(Title).lower():
                try:
                    UserPostHistory = reddit.redditor("{}".format(User)).submissions.new()
                    UserFlair.CooldownChecker(User, UserPostHistory, GoG)
                                    
                except Exception as e:
                    print(datetime.datetime.now(), "GOG threads", e, traceback.format_exc())

    except Exception as e:
        print(datetime.datetime.now(), "Posts", e, traceback.format_exc())
                    
###-----Checks when user comments in Offer--------------------------------------------------------------
    try:
    # commented out section is for history check
    # for submission in GoG.new(limit=None):
        # submission.comments.replace_more(limit=None) 
        # for comment in submission.comments.list():
        print(datetime.datetime.now(), 'Starting Comments check...')
        for comment in GoG.stream.comments(pause_after=-1):
            if comment is None:
                time.sleep(180)
                break
            
            RequestOrComment = "Comment"
            User = comment.author
            PostID = comment.id
            PostParentID = comment.submission.id
            BodyText = comment.body
            Title = comment.submission.title

            if User=="OurRobotOverlord" or User=="AutoModerator":
                continue
            PostLogLine = "https://reddit.com/comments/" + str(PostParentID) + "/" + str(User) +"/" + str(PostID)
            if PostLogLine in GoG.wiki["postlog"].content_md:
                continue
            WikiWrite.WriteWiki("postlog", PostLogLine, GoG)

            comment.refresh() #required; no clue why
        
            #Normalizes parent flair type
            if comment.is_root==True:
                parent=comment
            else:
                parent=comment.parent()
                while parent.is_root==False:
                    parent=parent.parent()

            GiftLog.GiftCheck(BodyText, comment, User, parent, reddit, GoG)    
                    
            ##Below is a check to make sure it's not checking comments by bots as to not waste time/resources OR the author of the thread
            if "[offer]" not in str(Title).lower() or User in ModList or comment.is_submitter==True: #intentionally runs at this time; do not move
                continue
            elif "Not entering" in BodyText or "Not participating" in BodyText or "Not taking part" in BodyText or comment.is_root is False:
                continue

            else:
#                 print("Offer comment")
                RequestOrComment = "Comment"
                Delay = time.time() - comment.created_utc
                if comment.banned_by!=None or comment.removed is True:
                    continue
                if Delay > 90:
                    try:
#                         print('Starting ReceiversGamingPlatform.ProfileChecker')
                        ReceiversGamingPlatform.ProfileChecker(User, BodyText, RequestOrComment, PostID, GoG)
                        
##                        print('Starting HistoryCheck.HistoryKarmaCheck')
                        UserComments = reddit.redditor("{}".format(User)).comments.top(limit=None)
                        HistoryCheck.HistoryKarmaCheck(User, UserComments, KarmaSubs, RequestOrComment, PostID)
                        

##                        print('Starting HistoryCheck.HistoryGiveawayCheck')
                        UserGiveawayHistory = reddit.redditor("{}".format(User)).new(limit=PostHistory)
                        HistoryCheck.HistoryGiveawayCheck(User, UserGiveawayHistory, GiveawaySubs, RequestOrComment, PostID)
                    
                    except Exception as e:
                        print(datetime.datetime.now(), "Comments", e, traceback.format_exc())

    except Exception as e:
           print(e, traceback.format_exc())
           time.sleep(3)
           continue
