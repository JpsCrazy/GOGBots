import Remover
import time
import traceback
from steam.steamid import SteamID

#local
import SteamBot
 
PlatformIDList = dict(Steam="",GOG="",PSN="",Xbox="",Switch="",ThreeDS="",EA_ID="",Itch="")
PlatformRecordedIDList = dict(RecordedSteam="",RecordedGOG="",RecordedPSN="",RecordedXbox="",RecordedSwitch="",RecordedThreeDS="",RecordedEA_ID="",RecordedItch="")

def ProfileChecker(User, BodyText, RequestOrComment, PostID, GoG):
    try:
        import re
        RemovalReason = None

        UserIDSearch = re.search(r"(?i)((https{0,1}://){0,1}(www\.){0,1}(steamcommunity\.com\/(profiles|id)\/[^!\(\)\[\]/\s]*|gog\.com\/u\/[^!\(\)\[\]/\\\s]*|my\.playstation\.com/profile/[^!\(\)\[\]/\\\s]*|psnprofiles\.com/[^!\(\)\[\]/\\\s]*|\/profile\?gamertag=[^!\(\)\[\]/\\\s]*|mygamerprofile\.net[^!\(\)\[\]/\\\s]*|xboxgamertag\.com\/search\/[^!\(\)\[\]/\\\s]*|(SW){0,1}-{0,1} {0,1}([0-9]{4}-){2}[0-9]{4}|(?!https:\/\/\S*?\.itch\.io\/[A-Z,0-9])https:\/\/\S*?\.itch\.io|epicgames.com\/\S*\/u\/(\S*)))", str(BodyText))
        if UserIDSearch is None:
            # print("No ID found for ", User)
            return
        UserID = UserIDSearch.group(1).replace("\\", "")
##        print(UserID)
        
        if "steamcommunity.com" in UserID.lower():
            ID64Check = re.search(r"(?i)(id|profiles)/([^!\(\)\[\]/\s]*)", UserID.lower())
            if ID64Check is None:
                print("ID64 check broken; skipping user", UserID)
                return

            ID64 = ID64Check.group(2)
#                     print('DEBUG:', UserID, ID64)
            if ID64.isdigit() is False:
#                         print(ID64)
                ID64 = str(SteamID.from_url(UserID))
                UserID = "https://steamcommunity.com/profiles/" + ID64
                if ID64 != "None":
                    SteamBot.SteamSanitizer(User, UserID, ID64, PlatformIDList, PostID, RequestOrComment)
                else:
                    time.sleep(180)
                    ID64 = str(SteamID.from_url(UserID))
                    if ID64 == "None":
                        print("ID64 converter broken; skipping", UserID)
                        return
                    SteamBot.SteamSanitizer(User, UserID, ID64, PlatformIDList, PostID, RequestOrComment)
                    

        elif "gog.com" in UserID.lower():
            PlatformIDList["GOG"] = UserID
        elif "@" in UserID:
            PlatformIDList["EA_ID"] = UserID
        elif "my.playstation.com" in UserID.lower() or "psnprofiles.com" in UserID.lower():
            PSNProfile = re.search(r"(psnprofiles\.com/|my\.playstation\.com/profile/)([^/\s]*)", UserID)
            if PSNProfile is None:
                print("Error with PSN profiles", UserID)
            PlatformIDList["PSN"] = "https://psnprofiles.com/" + PSNProfile.group(2)
        elif "/profile?gamertag=" in UserID.lower() or "mygamerprofile" in UserID.lower() or "xboxgamertag.com" in UserID.lower():
            XboxProfile = re.search(r"(?i)(/profile\?gamertag=|xboxgamertag\.com/search/|mygamerprofile\.net/gamer/)([^/\s]*)", UserID)
            if XboxProfile is None:
                print("Error with Xbox/Microsoft profiles", UserID)
            PlatformIDList["Xbox"] = "https://www.xboxgamertag.com/search/" + XboxProfile.group(2)
        elif UserID.lower().replace("sw","").replace("-","").isdigit() is True:
            if "sw" in UserID.lower():
                PlatformIDList["Switch"] = UserID
            else:
                PlatformIDList["ThreeDS"] = UserID
        elif "itch.io" in UserID.lower():
            PlatformIDList["Itch"] = UserID
#             UserProfileHistory = GoG.wiki["userprofilehistory"]
#             UserProfileSearch = re.search(rf"(?i)(u/{User}\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?))", UserProfileHistory.content_md)
#             UserLine = "u/" + str(User) + "|" + PlatformIDList["Steam"] + "|" + PlatformIDList["GOG"] + "|" + PlatformIDList["PSN"] + "|" + PlatformIDList["Xbox"] + "|" + PlatformIDList["Switch"] + "|" + PlatformIDList["ThreeDS"] + "|" + PlatformIDList["EA_ID"] + "|" + PlatformIDList["Itch"]
#             if UserProfileSearch is None:
#                 UpdatedList = str(UserProfileHistory.content_md) + "\n" + UserLine
#                 print("Creating record of profile for", str(User))
#                 UserProfileHistory.edit(content=UpdatedList, reason="Adding user profile")
#             else:
#                 Num=1
#                 for p,r in zip(PlatformIDList,PlatformRecordedIDList):
#                     Num = Num+1
#                     if Num > len(PlatformIDList):
#                         break
#                     PlatformRecordedIDList[r]=str(UserProfileSearch.group(Num))
#                     if PlatformIDList[p] != "" and PlatformRecordedIDList[r] != "":
#                         if PlatformIDList[p] != PlatformRecordedIDList[r]:
#                             AltID=p
#                             print(AltID, "alt account detected for", User, PlatformRecordedIDList[r], UserID, "- removing post.")
#                             RemovalReason = "Alt"
#     ##                      GeneralRemove()
#                             AltID = None
#                             break
#                     elif PlatformRecordedIDList[r] != "" and PlatformIDList[p] == "":
#                         PlatformIDList[p] = PlatformRecordedIDList[r]
#                         UserLine = "u/" + str(User) + "|" + PlatformIDList["Steam"] + "|" + PlatformIDList["GOG"] + "|" + PlatformIDList["PSN"] + "|" + PlatformIDList["Xbox"] + "|" + PlatformIDList["Switch"] + "|" + PlatformIDList["ThreeDS"] + "|" + PlatformIDList["EA_ID"] + "|" + PlatformIDList["Itch"]
#                 if UserProfileSearch.group(1) != UserLine:
#                     print("Updating recorded profile for", str(User))
#                     UpdatedList = str(UserProfileHistory.content_md).replace(UserProfileSearch.group(1),UserLine)
#                     UserProfileHistory.edit(content=UpdatedList, reason="Adding user profile")
#                     UserLine = None
#                 else:
#     ##                print(str(User) + "'s records are up to date")
#                     pass

            
    except Exception as e:
        print(ProfileChecker, e, traceback.format_exc())