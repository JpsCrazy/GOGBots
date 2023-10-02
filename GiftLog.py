import re
import traceback
import datetime

import UserFlair

PlatformList = "Steam", "Switch", "PSN", "PS3", "PS4", "PS5", "PS6", "PS7", "PS8", "PS9", "Xbox", "Microsoft"

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

def GiftCheck(BodyText, comment, User, parent, GoG):
###--Checks for !gift commands
    print(BodyText)
    Gift = re.findall(r'(?i)!gift\s*/{0,1}u{0,1}/{0,1}(\S*)\s*([^\n]*)', str(BodyText))
    if Gift is not None:
        GiftCommandNum = -1
        for GiftCommand in Gift:
            GiftCommandNum = GiftCommandNum+1
            if GiftCommandNum > len(Gift):
                break

            Giftee = str(Gift[GiftCommandNum][0]).replace("\\","")
            GiftItem = str(Gift[GiftCommandNum][1])
            
            if User == Giftee.lower():
                print(User + " attempted to gift to themself; ignoring")
                continue

            Day = datetime.datetime.fromtimestamp(comment.created_utc).strftime("%d")
            Month = datetime.datetime.fromtimestamp(comment.created_utc).strftime("%m")
            Year = datetime.datetime.fromtimestamp(comment.created_utc).strftime("%Y")
            Title = comment.submission.title
            Platform = re.match(r'(?i)\[\S*] {0,9}\[(\S*)]', Title)
            if Platform is None:
                for i in PlatformList:
                    print(i, GiftItem)
                    if i.lower() in GiftItem.lower():
                        Platform = i
                        break
                if Platform is None:
                    Platform = "unspecified platform"
            else:
                Platform = str(Platform.group(1))
            
            writeGiftLog(User, Giftee, GiftItem, Platform, Day, Month, Year, GoG)
            UserFlair.FlairAssigner(User, Giftee, comment, parent, GoG)
            return Giftee