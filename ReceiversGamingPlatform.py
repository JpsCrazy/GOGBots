import Remover
import time
import requests
import json
import traceback
from steam.steamid import SteamID

#local
import SteamBot
from SteamAPIKey import SteamAPIKey
 
PlatformIDList = dict(Steam="",GOG="",PSN="",Xbox="",Switch="",EA_ID="",Itch="")
PlatformRecordedIDList = dict(RecordedSteam="",RecordedGOG="",RecordedPSN="",RecordedXbox="",RecordedSwitch="",RecordedEA_ID="",RecordedItch="")

def ProfileChecker(User, BodyText, RequestOrComment, PostID, GoG):
    try:
        import re
        RemovalReason = None

        UserIDSearch = re.search(r"(?i)((?:http)?s?(?:://)?(?:www\.)?(steamcommunity\.com\/(profiles|id)\/|gog\.com\/u\|my\.playstation\.com/profile/|psnprofiles\.com/|\/profile\?gamertag=|mygamerprofile\.net|xboxgamertag\.com\/search\/|(?:SW)?-{0,1} {0,1}(?:[0-9]{4}-){2}[0-9]{4}|(?!https:\/\/\S*?\.itch\.io\/[A-Z,0-9])https:\/\/\S*?\.itch\.io|epicgames.com\/\S*\/u\/|[^!\(\)&\[\]/\s]*(?:#|@) ?|ubisoftconnect\.com/\S*/profile/)([^!\(\)&\[\]/\s]*)/?)", str(BodyText))
        if UserIDSearch is None:
          return
        if UserIDSearch.group(4) is None:
            print("ID found but incomplete ", UserIDSearch.group(1))
            return
        UserID = UserIDSearch.group(1).replace("\\","")
        # print(UserID, PostID, RequestOrComment)
        
        if "steamcommunity.com" in UserID.lower():
            ID64 = UserIDSearch.group(4).replace("\\","")
            UserID = "https://www.steamcommunity.com/" + UserIDSearch.group(3) + "/" + ID64
            print(User, PostID, RequestOrComment, str(ID64))
            if ID64.isdigit() is False or len(ID64) != 17:
                try:
                    ID64Checker = requests.get("https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=" + SteamAPIKey + "&vanityurl=" + ID64)
                    ID64JSON = ID64Checker.json()
                    ID64 = ID64JSON['response']['steamid']
                except Exception as e:
                    print("ID64 Converter", e, traceback.format_exc())
                UserID = "https://steamcommunity.com/profiles/" + ID64
            SteamBot.SteamSanitizer(User, PostID, RequestOrComment, str(ID64))
            
    except Exception as e:
        print(ProfileChecker, e, traceback.format_exc())
