#!/usr/bin/python
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

reddit = praw.Reddit('GOGThreadChecker', user_agent='GOGThreadChecker_5.0b')
GoG = reddit.subreddit("GiftofGames")
GiftLog = GoG.wiki['giftlog'].content_md
GoGThreadLog = GoG.wiki['gogthreadlog'].content_md

print("Starting GOG Thread Checker bot...")
while True:
    try:
        Today = datetime.today()
        for line in GiftLog.splitlines():
            line = line.strip().lower()
            if re.search('^\s*$',line) is not None:
                continue
            # Search wiki for gift
                    
            GOGLine = re.search('(?i)(\S*?) gifted (\S*?)? (.*?)? ?for (.*?) on (\d{1,2}/\d{1,2}/\d{2,4})$', line)
            if GOGLine is None:
                print("Error finding gift in line", line)
                continue
                    
            Gifter = GOGLine.group(1)
            GifterEscaped = re.escape(Gifter)
            if str(Gifter).lower() in ("ourrobotoverlord"):
                print("Gift from ourrobotoverlord detected. Likely error; skipping.")
                continue

            Giftee = GOGLine.group(2)
            if Giftee is None:
                print("Missing Giftee; skipping", line)
                continue
            GifteeLinked = re.search (r'(?i)reddit\.com/(?:u|user)/(\S*)/', Giftee)
            if GifteeLinked is not None:
                Giftee = GifteeLinked.group(1).replace("\\","")

            Gift = GOGLine.group(3).lower()
            if Gift in ("free trial", "beta"):
                print("Temporary access gift; skipping")
                continue

            Platform = GOGLine.group(4)

            GiftDate = datetime.strptime(GOGLine.group(5), '%d/%m/%Y')

            ThreeDaysAfter = GiftDate + timedelta(days=3)
            if Today < ThreeDaysAfter:
                # print("Less than 3 days since gift; skipping")
                continue

            GiftDateBacklog = GiftDate + timedelta(HistoryBackdateDays)
            if Today > GiftDateBacklog:
                # print(Gift, "from", Gifter, "to", Giftee, "too old to enforce. Skipping.")
                continue

            GiftLogBanned = Giftee + ' received ' + Gift + ' from ' + Gifter + ' BANNED'
            ##    print("Checking server ban list")
            if any(GoG.banned(redditor=Giftee)):
                # print(Giftee, "is banned.")
                WikiWrite.WriteWiki("gogthreadlog", GiftLogBanned, GoG)
                continue
            
            GiftLogError = Giftee + ' received ' + Gift + ' from ' + Gifter + ' ERROR'
            if ValidUser.ValidUserCheck(reddit, Giftee) != 1:
                # print(Giftee, "is no longer valid")
                WikiWrite.WriteWiki("gogthreadlog", GiftLogError, GoG)
                continue

            GOGLineFound = Giftee + ' received ' + Gift + ' from ' + Gifter + ' COMPLETED'
            GOGLineReminded = Giftee + ' received ' + Gift + ' from ' + Gifter + ' REMINDED'
            GOGLineRemindedEscaped = re.escape(GOGLineReminded)
            GOGLineRemindedwDate = GOGLineReminded + ' ' + str(Today)
            
            if (GOGLineFound or GiftLogBanned or GiftLogError) in GoGThreadLog:
                # print("GOG post or known error found")
                continue

            ##    print("Checking", Giftee, "for", Gift, "from", Gifter)     
            GOGFound = False
            try:
                #SearchQuery = f'title:"[GOG]" author:"{Giftee}"'
                #UserPosts = GoG.search(SearchQuery, sort="new", time_filter="month") ##Searches for [GOG] tags by the giftee for the gifter. Prone to false negatives.
                UserPosts = reddit.redditor(Giftee).submissions.new() ##Returns posts from receiver
                for post in UserPosts:
                    if post is None:
                        break

                    GracePeriod = GiftDate - timedelta(days=3)
                    print(post.title, post.created_utc, Gifter, GracePeriod.timestamp())
                    if post.created_utc < GracePeriod.timestamp():
                        #print('Submissions older than gift date; end')
                        break
                    
                    if post.subreddit != "GiftofGames":
                        #print('Wrong sub; skip')
                        continue

                    GOGThread = re.search(rf'(?i)^\s*\[GOG\].*({Gifter}|{GifterEscaped})', post.title)
                    if GOGThread is not None:
                        print('New GOG thread found', str(post.title), Giftee, Gifter)
                        GOGFound = True
                        #WikiWrite.WriteWiki("gogthreadlog", GOGLineFound, GoG)
                        break

            except PrawcoreException as e:
                if "404" in str(e):
                    print(Giftee, "deleted their account. Skipping future checks.")
                    WikiWrite.WriteWiki("gogthreadlog", GiftLogError, GoG)
                    
                elif "403" in str(e):
                    print(e, Giftee)
                else:
                    print(e, Giftee)

            if GOGFound == True:
                continue

            RemindDateSearch = re.search(fr"(?i){GOGLineRemindedEscaped} (\d{4}-\d{2}-\d{2}).*?\n", GoGThreadLog)
            if RemindDateSearch is not None:
                RemindDate = datetime.strptime(RemindDateSearch.group(1), '%Y-%m-%d')
                SevenDaysAfter = RemindDate + timedelta(days=4)
                if Today < SevenDaysAfter:
                    continue
                print("No GOG thread for", Gifter, "by", Giftee, "found after reminding. Banning.")
                # GoG.banned.add(Giftee, ban_reason='No GOG thread', duration=BanLength, ban_message='**Reason:** No [GOG] thread post found to thank {} for {}. \n\nPlease read the [full rules](https://www.reddit.com/r/GiftofGames/wiki/rules) \n\nThis action was performed by a bot. Please reply to this message if you believe this action was made in error'.format(Gifter,Gift))
                # WikiWrite.WriteWiki("gogthreadlog", GOGLineFound, GoG)
                continue
                    
            elif Today > ThreeDaysAfter:
                try:
                    print("No GOG thread for", Gifter, "by", Giftee, "found. Sending reminder.")
                    # WikiWrite.WriteWiki("gogthreadlog", GOGLineRemindedwDate, GoG)
                    # GoG.modmail.create(subject="Reminder to post [GOG] thread", body="As a reminder, **all** gifts received on this subreddit require you to post a [GOG] thank you thread ***with the gifter's username in the title***. \n\nNo [GOG] thank you thread to {} for {} found. Failure to post one will result in a ban. \n\nNo response to this message is needed unless you believe it was made in error. This message was sent by a bot.".format(Gifter,Gift), recipient="{}".format(Giftee))
                except Exception as e:
                    print(e)
                continue

            else:
##                print("Giving", Giftee, "until", ThreeDaysAfter, "before reminding.")
                continue
        # print('Checks complete')
        time.sleep(14400)        
                    
    except Exception as e:
        print(e, Giftee, traceback.format_exc())

