#!/use/bin/python

import datetime
import praw
import re
import traceback

#local
import ValidUser

def RemoveLog(WikiContent, Line):
    WikiContent = str(WikiContent).replace(Line,"").replace("\n\n\n","\n\n")
    return WikiContent

def CooldownRemover(reddit, GoG):
    print(datetime.datetime.now(), "Starting Cooldown Remover...")
    try:
        Wiki = GoG.wiki["cooldownlog"]
        WikiContent = Wiki.content_md.strip()
        for line in WikiContent.splitlines():
            if len(line) == 0: #if line is empty, skip
                continue
            CooldownInfo = re.search(rf"(?i)([^\s]*) (.*) \|\| ([^\s]*) \|\| (\d\d\d\d-\d\d-\d\d)", line)
            User = CooldownInfo.group(1)
            FlairText = CooldownInfo.group(2)
            FlairCSS = CooldownInfo.group(3)
            CooldownDate = datetime.datetime.strptime(CooldownInfo.group(4), "%Y-%m-%d")
            Today = datetime.datetime.today()
            TimeDiff = (Today - CooldownDate).days
            Voided = ValidUser.ValidUserCheck(reddit, User)
            # print(Voided, User)
            if Voided == 0:
                print(User, "not found, removing from log")
                Line = str(CooldownInfo.group(0).strip())
                RemoveLog(WikiContent, line)
                continue
            if Voided == 2:
                print(User, "ERROR!")
                Line = str(CooldownInfo.group(0).strip())
                RemoveLog(WikiContent, line)
                continue

            
            if TimeDiff > 30:
                print("Removing " + User + " from cooldown and resetting flair to " + FlairText)
                try:
                    pass
                    GoG.flair.set(User, text=FlairText, css_class=FlairCSS)
                    GoG.modmail.create(subject="Removed from cooldown in r/GiftofGames", body=str("Your cooldown has been removed. \n\nYou may now make a [REQUEST] or enter an [OFFER] and your flair has been restored to " + FlairText + ". \n\nThis action was performed by a bot."), recipient=User)
                    WikiContent = RemoveLog(WikiContent, line.strip())
                except Exception as e:
                    print("Error resetting flair for", User, "\n", e, traceback.format_exc())
                    
        # print("Bringing wiki current")
        Wiki.edit(content=WikiContent, reason="Cooldown Removals")
    except Exception as e:
        print(e, traceback.format_exc())
