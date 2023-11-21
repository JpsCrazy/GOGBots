import re
import traceback
import datetime

import UserFlair
import ValidUser

PlatformList = "Steam", "Switch", "PSN", "PS3", "PS4", "PS5", "PS6", "PS7", "PS8", "PS9", "Xbox", "Microsoft", "Epic", "EGS", "Nintendo"

def writeGiftLog(Gifter, Giftee, GiftItem, Platform, Day, Month, Year, GoG):
    try:
        import WikiWrite
        GiftLine = str(str(Gifter) + " gifted " + str(Giftee) + " " + str(GiftItem) + " for " + str(Platform) + " on " +  Day + "/" + Month + "/" + Year)
        WikiWrite.WriteWiki("giftlog", str(GiftLine), GoG)
        #writeGiftLogDB(Gifter, Giftee, GiftItem, Platform, Day, Month, Year)
    except Exception as e:
            print("writeGiftLog():", e, traceback.format_exc())
            
def writeGiftLogDB(Gifter, Giftee, GiftItem, Platform, Day, Month, Year):
    try:
        ##database support
        if "'" in GiftItem:
            GiftItem = GiftItem.replace("'",r"\'")
        dbcursor.execute("INSERT INTO GiftLog VALUES('%s', '%s', '%s', '%s', '%s');" % (str(Giftee), str(GiftItem)[0:127], str(Gifter), str(Platform), (Year + "-" + Month + "-" + Day)))
        mydb.commit();
    except Exception as e:
            print("writeGiftLogDB():", e, traceback.format_exc())

def GiftCheck(BodyText, comment, User, parent, reddit, GoG):
###--Checks for !gift commands
    comment.refresh()
    # print(BodyText)
    AlreadyFlaired = False
    if len(comment.replies) > 0: #if more than 0 comments on a comment
        for reply in comment.replies:
            if reply.author == "OurRobotOverlord":
                if "flair" in str(reply.body).lower() or "gifted" in str(reply.body).lower():
                    AlreadyFlaired = True
    if AlreadyFlaired == True:
        print("Gift flair already processed")
        return
    Gift = re.findall(r'(?i)!gift\s*/?(?:u/)?(\S*)\s*([^\n]*)', str(BodyText))
    if str(Gift) != "[]":
        GiftCommandNum = -1
        for GiftCommand in Gift:
            GiftCommandNum = GiftCommandNum+1
            if GiftCommandNum > len(Gift):
                break

            Giftee = str(Gift[GiftCommandNum][0]).replace("\\","")
            GiftItem = str(Gift[GiftCommandNum][1])
            if Giftee is None:
                print("Gift but no giftee; probable error")
                continue
            if ValidUser.ValidUserCheck(reddit, Giftee) == 0:
                print(str(User), "attempted to gift", str(Giftee), "but they do not exist")
                comment.reply("Unable to flair u/" + str(Giftee) + " as their profile does not seem to exist. Please double check your spelling and try again. \n\nPlease [contact the moderators](https://www.reddit.com/message/compose?to=%2Fr%2FGiftofGames) if you believe this action was made in error.")
                continue 
            if User == Giftee.lower():
                print(User + " attempted to gift to themself; ignoring")
                continue

            # print(User, Giftee, GiftItem)
            Day = datetime.datetime.fromtimestamp(comment.created_utc).strftime("%d")
            Month = datetime.datetime.fromtimestamp(comment.created_utc).strftime("%m")
            Year = datetime.datetime.fromtimestamp(comment.created_utc).strftime("%Y")
            Title = comment.submission.title
            Platform = re.match(r'(?i)\[\S*] {0,9}\[(\S*)]', Title)
            if Platform is None:
                for i in PlatformList:
                    if i.lower() in GiftItem.lower():
                        Platform = i
                        break
                if Platform is None:
                    Platform = "unspecified platform"
            else:
                Platform = str(Platform.group(1))
            
            # print(User, Giftee, GiftItem, Platform, Day, Month, Year, GoG)
            writeGiftLog(User, Giftee, GiftItem, Platform, Day, Month, Year, GoG)
            UserFlair.FlairAssigner(User, Giftee, comment, parent, GoG)
        
    else:
        # print("No gift found", BodyText)
        return