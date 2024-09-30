import datetime
import time
import praw
import re
import traceback

import ValidUser
import WikiWrite

def doFlair(gifter,gifted,comment,GoG):
    #Grabs their flairs via the Reddit API
    gifterflair=next(GoG.flair(gifter))['flair_text']
    receiverflair=next(GoG.flair(gifted))['flair_text']
    newgifterflair=""
    newreceiverflair=""
    rcount=0
    gcount=0 #count for gifter if they have a grabbed flair as well
    gclass="" #Gifter flair class
    rclass="" #Receiver flair class
    
    #The below block of code flairs the gifter based on their current flair
    if gifterflair=="" or gifterflair is None:
        newgifterflair="Gifted"
        gclass="gifted2"
        
    elif "Gifted" in gifterflair:
        newgifterflair="No flair change"
        gclass="gifted2"
    
    elif "Grabbed" in gifterflair:
        newgifterflair="Gifted | " + gifterflair
        gcount=int(str(gifterflair.split("Grabbed ")[1]).replace("+",""))
        if gcount <=9:
            gclass="giftedgrabbed2"
        elif gcount <=19:
            gclass="giftedgrabbed3"
        elif gcount <=29:
            gclass="giftedgrabbed4"
        elif gcount > 29:
            gclass="giftedgrabbed5"
    
    if newgifterflair!="No flair change":
        GoG.flair.set(gifter,newgifterflair,gclass)
        
#     print("Gifter " + gifter + "'s, new flair is " + newgifterflair + " with flair class " + gclass)

#     print(gifted, receiverflair)
    #The below block of code flairs the receiver based on their flair
    if receiverflair=="" or receiverflair is None:
        newreceiverflair="Grabbed 1"
        rcount=1
        rclass="nes"
    elif receiverflair.replace(" ","")=="Gifted":
        newreceiverflair= "Gifted | Grabbed 1"
        rclass="giftedgrabbed2"
        rcount=1
    elif "Gifted | Grabbed" in receiverflair:
        newreceiverflair="Gifted | Grabbed " + str(int(receiverflair.split("Gifted | Grabbed ")[1].replace(" ","").replace("+",""))+1)
        rcount=int(receiverflair.split("Gifted | Grabbed ")[1].replace(" ","")) + 1
        if rcount <=9:
            rclass="giftedgrabbed2"
        elif rcount <=19:
            rclass="giftedgrabbed3"
        elif rcount <=29:
            rclass="giftedgrabbed4"
        elif rcount > 29:
            rclass="giftedgrabbed5"
            
    elif "Grabbed" in receiverflair:
        newreceiverflair="Grabbed " + str(int(receiverflair.split("Grabbed ")[1].replace(" ","").replace("+",""))+1)
        rcount=int(receiverflair.split("Grabbed ")[1].replace(" ",""))+1
        if rcount <=9:
            rclass="nes"
        elif rcount <=19:
            rclass="snes"
        elif rcount <=29:
            rclass="n64"
        elif rcount > 29:
            rclass="gamecube"
    GoG.flair.set(gifted ,newreceiverflair,rclass)
#     print("Receiver " + gifted + "'s, new flair is " + newreceiverflair + " with flair class " + rclass)
    #Sort out flair classes for both the receiver and gifter

    comment.reply(str(gifter) + " gifted " + str(gifted) + " whose new flair is " + str(newreceiverflair))

def doCooldown(UserToCooldown, GoG):
    #!!! should really pass reddit down instead of re-creating it
    reddit = praw.Reddit('GOGUserHistoryBot', user_agent='GOGUserHistoryBot_1.9')
    if ValidUser.ValidUserCheck(reddit, UserToCooldown) != 1:
        UserToCooldown = ''
        return
    if any(GoG.banned(redditor=UserToCooldown)) == True:
        UserToCooldown = ''
        return
    if "cooldown" in str(next(GoG.flair("{}".format(UserToCooldown)))['flair_text']).lower():
        GoG.modmail.create(subject="Possible Cooldown Issue", body=f"{UserToCooldown} triggered cooldown twice; flair check", recipient='JpsCrazy')
        UserToCooldown = ''
        return
    
    ExistingCooldownSearch = re.search(f'{UserToCooldown}(.*Grabbed (\d*).*)\n', GoG.wiki["cooldownlog"].content_md)
    if ExistingCooldownSearch is not None:
        ExistingFlair = ExistingCooldownSearch.group(1)
        ExistingGrabbedCount = "Grabbed " + ExistingCooldownSearch.group(2)
        NewGrabbedCount = "Grabbed " + str(int(ExistingCooldownSearch.group(2))+1)
        UpdatedFlair = ExistingFlair.replace(ExistingGrabbedCount,NewGrabbedCount)
        #this is incomplete. Create wiki update?



    if UserToCooldown in GoG.wiki["cooldownlog"].content_md:
        GoG.modmail.create(subject="Possible Cooldown Issue", body=f"{UserToCooldown} triggered cooldown twice; flair check", recipient='JpsCrazy')
        UserToCooldown = ''
        return

    try:
        Date = datetime.date.today()
        if str(next(GoG.flair("{}".format(UserToCooldown)))['flair_text']) is None:
            TextAndCSS = "Grabbed 1" + " || " + "nes"
        else:
            TextAndCSS = str(next(GoG.flair("{}".format(UserToCooldown)))['flair_text']) + " || " + str(next(GoG.flair("{}".format(UserToCooldown)))['flair_css_class'])
        CooldownLine = str(UserToCooldown) + " " + TextAndCSS + " || " + str(Date)
        print(str(UserToCooldown) + " is being put on cooldown")
        WikiWrite.WriteWiki("cooldownlog", str(CooldownLine), GoG)
        GoG.flair.set(UserToCooldown, text='Cooldown', css_class='cooldown')
        GoG.modmail.create(subject="Being put on cooldown in r/GiftofGames", body="You have been put on a cooldown after receiving a number of games in a relatively short span of time. \n\nYou may still particpate on the subreddit, however you will be unable to enter an [OFFER] or make a [REQUEST] for 30 days. \n\nThis action was performed by a bot. Please reply to this message if you believe this action was made in error.", recipient=UserToCooldown)
    except Exception as e:
        print(time.strftime("%H:%M"),' Exception:', e, traceback.format_exc())

def CooldownChecker(User, UserPostHistory, GoG, RecentGOGPosts=0):

    for post in UserPostHistory:
        if post is None:
            break
        if post.banned_by!=None:
            continue
        if post.subreddit != "GiftofGames":
            continue
        OneMonth = 86400*30 #86400 seconds is 1 day
        TimeDifference = int(time.time())-int(post.created_utc)
        if TimeDifference > OneMonth:
            break
        if "[request]" in str(post.title).lower():
            continue
        if "[offer]" in str(post.title).lower():
            continue
        if "[intro]" in str(post.title).lower():
            continue
        if "[discussion]" in str(post.title).lower():
            continue
        if "[gog]" in str(post.title).lower():
            RecentGOGPosts = RecentGOGPosts+1
            if RecentGOGPosts >= 3:
                if "cooldown" not in str(next(GoG.flair("{}".format(User)))['flair_text']).lower():
                    print("Putting", str(User), "on cooldown")
                    doCooldown(str(User), GoG)

def FlairAssigner(User, Giftee, comment, parent, GoG):
    ###--Assigns user flair from !gift commands
    if "cooldown" not in str(next(GoG.flair("{}".format(Giftee)))['flair_text']).lower():
        LinkFlairText = parent.parent().link_flair_text
        if LinkFlairText=="REQUEST" or LinkFlairText=="CLOSED REQUEST":
            parent.parent().flair.select("a02ee300-3db4-11eb-9965-0e3501162567")
            doFlair(str(User),str(parent.parent().author), comment, GoG)
            ##NEEDED: enable cooldown on Requests, below
            ##doCooldown(parent.parent().author, GoG)
            
        elif LinkFlairText=="OFFER" or LinkFlairText=="CLOSED OFFER":
            doFlair(str(User),(str(Giftee)), comment, GoG)
            
        elif LinkFlairText=="GOG":
            doFlair(str(User),str(parent.parent().author), comment, GoG)

    else:
        ###--If user already on Cooldown, update backed up flair instead of current flair
        Wiki = GoG.wiki["cooldownlog"]
        WikiContent = Wiki.content_md.strip()
        WikiContent = str(WikiContent).replace("\n\n\n","\n\n")
        for line in WikiContent.splitlines():
            if len(line) == 0: #if line is empty, skip
                continue
            if str(Giftee).lower() in str(line).lower():
                FlairInfo = re.search(r"(?i)(.*?) ((Gifted){0,1} {0,1}\|{0,1} {0,1}(Grabbed){0,1} {0,1}(\d{0,3})) \|\| (.*) \|\| (\d*-\d*-\d*)", str(line))
                if FlairInfo is not None:
                    CooldownUser = FlairInfo.group(1)
                    CooldownDate = FlairInfo.group(7)
                    if FlairInfo.group(3) is not None:
                        GiftedFlair = FlairInfo.group(3) + " | "
                    else:
                        GiftedFlair = ""
                    GrabbedNum = int(str(FlairInfo.group(5)).replace("+",""))+1
                    FlairCSS = FlairInfo.group(6)
                    print("Updating", str(Giftee) + "'s", "flair while on cooldown")
                    UpdatedCooldownFlair = str(Giftee) + " " + str(GiftedFlair) + "Grabbed " + str(GrabbedNum) + " || " + str(FlairCSS) + " || " + str(CooldownDate)
                    WikiContent = str(WikiContent).replace(line,UpdatedCooldownFlair).replace("\n\n\n","\n\n")
                    WikiUpdateReason = str("Updating " + Giftee)
                    Wiki.edit(content=WikiContent, reason=WikiUpdateReason)
            break
