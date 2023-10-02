#!/use/bin/python

import datetime
import praw
import re
import traceback

reddit = praw.Reddit('GOGCooldownFlairBot', user_agent='GOGCooldownFlairBot')
GoG = reddit.subreddit("GiftofGames")

print("User Reddit Cooldown Flair Checker bot starting...")
while True:
    try:
        for flair in GoG.flair(limit=None):
            user = flair['user'].name
            flair_css_class = flair['flair_css_class']
            flair_text = flair['flair_text']
            if flair_text is not None:
                if "cool" in flair_text.lower() and "down" in flair_text.lower() and "ban" not in flair_text.lower() and "ban" not in flair_css_class.lower():
                    CooldownedUsers = open('CooldownedUsers.txt', 'a')
                    CooldownLine = str(user) + " " + str(flair_text) + " || " + str(flair_css_class) + " || 2020-01-01\n"
                    CooldownedUsers.write(str(CooldownLine))
                    CooldownedUsers.close
                    print(CooldownLine)
        break
    except Exception as e:
        print(e, traceback.format_exc())
