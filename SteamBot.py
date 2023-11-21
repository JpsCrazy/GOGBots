import traceback
import requests
import json

#local
from SteamAPIKey import SteamAPIKey
import Remover

def SteamSanitizer(User, PostID, RequestOrComment, ID64):
    try:
        ProfileVisibility = requests.get("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=" + SteamAPIKey + "&steamids=" + ID64)
        ProfileVisibilityJSON = ProfileVisibility.json()
    ##    print("\n DEBUG", ID64, UserIDSearch, ProfileVisibilityJSON, "\n")
        if ProfileVisibilityJSON['response']['players'][0]['communityvisibilitystate'] != 3 and ProfileVisibility.ok:
            RemovalReason = "Private Steam Profile"
            print(str(User) + "'s Steam profile is not visible; removing.")
            Remover.GeneralRemove(RequestOrComment, PostID, RemovalReason)
        LibraryVisibility = requests.get("http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?include_played_free_games=True&key=" + SteamAPIKey + "&format=json&steamid=" + ID64)
        LibraryVisibilityJSON = LibraryVisibility.json()
        if LibraryVisibilityJSON['response'] == {} and LibraryVisibility.ok:
            RemovalReason = "Private Steam Library"
            print(str(User) + "'s Steam library is not visible; removing.")
            Remover.GeneralRemove(RequestOrComment, PostID, RemovalReason)
        try:
            Level = requests.get("http://api.steampowered.com/IPlayerService/GetSteamLevel/v1/?key=" + SteamAPIKey + "&steamid=" + ID64)
            LevelJSON = Level.json()
            if str(LevelJSON) == "{'response': {}}" and Level.ok:
                return
            if int(LevelJSON['response']['player_level']) < 2:
                RemovalReason = "Low Steam Level"
                print(str(User) + "'s Steam level is less than 2; removing comment with Steam ID " + ID64)
                Remover.GeneralRemove(RequestOrComment, PostID, RemovalReason)
            if int(LevelJSON['response']['player_level']) is None:
                RemovalReason = "Low Steam Level"
                print(str(User) + "'s Steam level is not detected; removing comment with Steam ID " + ID64)
                Remover.GeneralRemove(RequestOrComment, PostID, RemovalReason)
        except Exception as e:
            print("SteamSanitizer Level", e, traceback.format_exc())
                
    except Exception as e:
        print("SteamSanitizer", e, traceback.format_exc())
