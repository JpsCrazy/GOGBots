#!/use/bin/python
import datetime
import praw
import time
import traceback
import re
#import mysql.connector

from prawcore.exceptions import NotFound

#local
import WikiWrite
import ValidUser

RequestBanLength = 7
GOGBanLength = 14
MaxBanLength = 90

#!!! add links to deleted posts?
def DeletionChecker(reddit, GoG, GoGdeletes):
    # print("GOG Deletion bot starting...")

    try:
        print(datetime.datetime.now(), "Starting Deletion check...")
        for submission in GoGdeletes.stream.submissions(pause_after=-1):
            if submission is None:
                break
            TimeDiff = time.time()-submission.created_utc
            SevenDays = 86400*7
            if TimeDiff > SevenDays:
                # print("End of new deletions...")
                break
            Title = submission.title
            PostID = submission.id
            if "gog" in Title.lower() or "request" in Title.lower():
                if "offer" not in Title.lower():
                    UserSearch = re.search('(?iu)\/u\/(\S*) \[(\S*( \S*){0,1})] was deleted from /r/GiftofGames on.* up (\S*) days', Title)
                    User = UserSearch.group(1)
                    Type = UserSearch.group(2)
                    TimeUp = UserSearch.group(4)
                    if TimeUp == "0.01":
                        continue
                    if any(GoG.banned(redditor=User)) == True:
                        print(User + " is already banned")
                        continue
                    PostLogLine = str(User) + " " + str(Type) + " " + str(PostID)
                    #TO-DO: Make one list, update wiki once
                    if PostLogLine in GoG.wiki["postlog/deletionpostlog"].content_md:
                        continue
                    WikiWrite.WriteWiki("postlog/deletionpostlog", PostLogLine, GoG)
                         
        # print("Beginning check for deletion bans...")
        BanList = ""
        DeletionPostLog = GoG.wiki["postlog/deletionpostlog"].content_md
        for line in DeletionPostLog.split("\n\n"):
            InitialLogSearch = re.search("(?i)^(\S*) (.*?) (\S*)$", line)
            if InitialLogSearch == None:
                # print("No ban found on line")
                continue
            SubjectUser = InitialLogSearch.group(1)
            if any(GoG.banned(redditor=SubjectUser)) == True:
                print(SubjectUser + " is already banned")
                continue
            if BanList is not None:
                if SubjectUser in BanList:
                    continue
            RequestSearch = re.findall(rf"(?iu){SubjectUser}.*REQUEST", DeletionPostLog)
            RequestCount = len(RequestSearch)
            GOGSearch = re.findall(rf"(?iu){SubjectUser}.*GOG", DeletionPostLog)
            GOGCount = len(GOGSearch)
            
            BanLength = (RequestCount*RequestBanLength)+(GOGCount*GOGBanLength)
            if BanLength > MaxBanLength:
                BanLength = MaxBanLength
            
            TempBanString = SubjectUser + " " + str(BanLength)
            BanList = BanList + TempBanString + "\n"
        
        RemovalMessageOpening = "Please read our [full rules](https://www.reddit.com/r/GiftofGames/wiki/rules).\n\n**Reason**: "
        RemovalMessageEnding = "\n\nThis action was automatically performed by a bot. Please [contact the moderators](https://www.reddit.com/message/compose?to=%2Fr%2FGiftofGames) if you believe this action was made in error."
        RemovalMessage = "Deletions are strictly prohibited as they can be viewed as evasion of rules. There are no exceptions for deleting an approved post; you must wait out your temporary ban."
        FullMessage = RemovalMessageOpening + RemovalMessage + RemovalMessageEnding
        for line in BanList.split("\n"):
            FinalSearch = re.search("(\S*) (\d*)", line)
            if FinalSearch == None:
                # print("No bans with days to issue")
                break
            UserToBan = FinalSearch.group(1)
            DaysToBan = FinalSearch.group(2)
            
            if any(GoG.banned(redditor=UserToBan)) == True:
                print(SubjectUser + " is already banned")
                continue
            
            if ValidUser.ValidUserCheck(reddit, UserToBan) == 1:
                print(UserToBan, "being banned for", DaysToBan, "days")
                try:
                    GoG.banned.add(UserToBan, ban_reason="Post Deletions", ban_note="Post Deletions", ban_message=FullMessage, duration=DaysToBan)
                except Exception as e:
                    print("Banning error", e)
            else:
                print(SubjectUser + "is not valid")
        
        # print("Bans completed; resetting wiki...")
        GoG.wiki["postlog/deletionpostlog"].edit(content="", reason="Reset After Banning")
            
    except Exception as e:
        print(e, traceback.format_exc())
