#!/use/bin/python
import re
import praw
from prawcore import PrawcoreException
import time
from datetime import timedelta, date, datetime
import datetime as dt
import os
from prawcore.exceptions import NotFound
import traceback
#local
import WikiWrite
import ValidUser

BanLength = 31
HistoryBackdateDays = 30

reddit = praw.Reddit('GOGThreadChecker', user_agent='GOGThreadChecker')
GoG = reddit.subreddit("GiftofGames")

print("Starting GOG Thread Checker bot...")

while True:
    try:
        Wiki = reddit.subreddit('GiftofGames').wiki['giftlog']
        Today = datetime.today()
        for line in Wiki.content_md.splitlines():
            line = line.strip()
            GOGLine = re.search('(?i)(\S*?) gifted (\S*?) (.*?) for (.*?) on (\d\d/\d\d/\d\d\d\d)$', line)
            if GOGLine is None:
                #print("Error finding gift", line)
                continue
            
            Gift = GOGLine.group(3).lower()
            
            if "beta" in Gift or "free trial" in Gift:
                continue
            
##                    print("Reading new line")
            Gifter = GOGLine.group(1)
            if "ourrobotoverlord" in str(Gifter).lower():
                Gifter = ""
            GifterEscaped = re.escape(Gifter)
            Giftee = GOGLine.group(2)
            Gift = GOGLine.group(3)
            Platform = GOGLine.group(4)

            GiftDate = datetime.strptime(GOGLine.group(5), '%d/%m/%Y')
            GiftDateBacklog = GiftDate + timedelta(HistoryBackdateDays)

            if Today > GiftDateBacklog:
##                print(Gift, "from", Gifter, "to", Giftee, "too old to enforce. Skipping.")
                continue

##                    print("Checking", Giftee, "for", Gift, "from", Gifter)           
##                        print("Checking server ban list")
            GiftLogError = Giftee + ' received ' + Gift + ' from ' + Gifter + ' ERROR'
            if any(reddit.subreddit("GiftofGames").banned(redditor=Giftee)):
                # print(Giftee, "is banned.")
                WikiWrite.WriteWiki("gogthreadlog", GiftLogError, GoG)
                continue

            if ValidUser.ValidUserCheck(reddit, Giftee) != 1:
                WikiWrite.WriteWiki("gogthreadlog", GiftLogError, GoG)
                continue

            GifteeLinked = re.search (r'(?i)reddit\.com/(?:u|user)/(\S*)/|\)', Giftee)
            if GifteeLinked is not None:
                Giftee = GifteeLinked.group(1).replace("\\","")
            
                   
            try:
##               print(Giftee, "not banned; proceeding.")
                GOGFound = False
                UserPosts = reddit.redditor("{}".format(Giftee)).submissions.new(limit=500) ##Returns top 500 posts from receiver
                for post in UserPosts:
##                    print(post.title)
                    if post is None:
                        continue
##                    print(post.title)
                    GOGThread = re.search(rf'(?i)\[GOG\].*({Gifter}|{GifterEscaped})', post.title)
                    if GOGThread is not None:
##                        print(str(post.title), Giftee, Gifter)
                        GOGFound = True
                        break
                ThreeDaysAfter = GiftDate + timedelta(days=3)
##                 print(Giftee, Today, ThreeDaysAfter)
                GOGLineFound = Giftee + ' received ' + Gift + ' from ' + Gifter + ' COMPLETED'
                GOGLineReminded = Giftee + ' received ' + Gift + ' from ' + Gifter + ' REMINDED'
                GOGLineRemindedEscaped = re.escape(GOGLineReminded)
                GOGLineRemindedwDate = GOGLineReminded + ' ' + str(Today)
                
                if GOGLineFound in GoG.wiki["gogthreadlog"].content_md:
                    continue

                if GiftLogError in GoG.wiki["gogthreadlog"].content_md:
                    continue
                
                if GOGFound == True:
                    WikiWrite.WriteWiki("gogthreadlog", GOGLineFound, GoG)
                    continue

                RemindDateSearch = re.search(fr"(?i){GOGLineRemindedEscaped} (\d\d\d\d-\d\d-\d\d).*?\n", GoG.wiki["gogthreadlog"].content_md)
                if RemindDateSearch is not None:
                    RemindDate = datetime.strptime(RemindDateSearch.group(1), '%Y-%m-%d')
                    SevenDaysAfter = RemindDate + timedelta(days=4)
                    if Today < SevenDaysAfter:
                        continue
                    print("No GOG thread for", Gifter, "by", Giftee, "found after reminding. Banning.")
                    reddit.subreddit("GiftofGames").banned.add(Giftee, ban_reason='No GOG thread', duration=BanLength, ban_message='**Reason:** No [GOG] thread post found to thank {} for {}. \n\nPlease read the [full rules](https://www.reddit.com/r/GiftofGames/wiki/rules) \n\nThis action was performed by a bot. Please reply to this message if you believe this action was made in error'.format(Gifter,Gift))
                    WikiWrite.WriteWiki("gogthreadlog", GOGLineFound, GoG)
                    continue
                        
                elif Today > ThreeDaysAfter:
                    try:
                        print("No GOG thread for", Gifter, "by", Giftee, "found. Sending reminder.")
                        reddit.subreddit("GiftofGames").modmail.create("Reminder to post [GOG] thread", "As a reminder, all gifts received on this subreddit require you to post a [GOG] thank you thread ***with the gifter's username in the title***. ([GOG] stands for GiftofGames; this is not solely for gog.com games) \n\nNo [GOG] thank you thread to {} for {} found. Failure to post one will result in a ban. \n\nNo response to this message is needed unless you believe it was made in error. This message was sent by a bot.".format(Gifter,Gift), "{}".format(Giftee))
                        if Giftee == "Nikhilkumar_001":
                            print(Giftee + '\n ' + 'GOGLineReminded' + '\n ' + GoG.wiki["gogthreadlog"].content_md)
                        WikiWrite.WriteWiki("gogthreadlog", GOGLineRemindedwDate, GoG)
                    except Exception as e:
                        print(e)
                    continue

                else:
##                    print("Giving", Giftee, "until", ThreeDaysAfter, "before reminding.")
                    continue

                
            except PrawcoreException as e:
                if "404" in str(e):
                    print(Giftee, "deleted their account. Skipping future checks.")
                    WikiWrite.WriteWiki("gogthreadlog", GiftLogError, GoG)
                elif "403" in str(e):
                    print(e, Giftee)
                else:
                    print(e, Giftee)

        time.sleep(3600)        
                    
    except Exception as e:
        print(e, Giftee, traceback.format_exc())
