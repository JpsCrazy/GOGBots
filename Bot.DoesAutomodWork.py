#!/use/bin/python
import praw
import time
import traceback
#import mysql.connector

from prawcore.exceptions import NotFound

##local files
import GiftLog
import HistoryCheck
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

ModList = "AutoModerator", "DjSoulFuck", "Saadieman", "freedomtacos", "Miniboyss", "Jaska95", "OurRobotOverlord", "JpsCrazy", "JpsCrazysBot", "fallen_fire", "MarioDesigns", "rollovertherainbow"
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

reddit = praw.Reddit('GOGDoesAutomodWork', user_agent='DoesAutomodWork')
GoG = reddit.subreddit("GiftofGames")

##--------------------------------------------------------------------
##--------------------------------------------------------------------
##-----------------START OF ACTUAL PROGRAM----------------------------
##--------------------------------------------------------------------
##--------------------------------------------------------------------

print("User Reddit History bot starting...")

Checked = " "
        
while True:
    try:
        print('Checking Requests')
        for submission in GoG.stream.submissions(pause_after=-1):
            if submission is None:
                time.sleep(15)
                break
            RequestOrComment = "Request"
            User = submission.author
            Title = str(submission.title).lower()
            PostID = submission.id
            Counter = 0
            if PostID in Checked:
                print("Complete")
                break
            if "gog" in Title:
                continue
            if "discussion" in Title:
                continue
            if "announcement" in Title:
                continue
            if "intro" in Title:
                continue
            
            for comment in submission.comments:
                if comment.author == 'AutoModerator':
                    Counter = Counter + 1
                    
            if Counter != 0:
                print("redd.it/" + PostID)
            Checked = Checked + " " + PostID
                
    except Exception as e:
        print(e)
            
            
       
