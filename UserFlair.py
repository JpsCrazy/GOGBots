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
    remoji=""
    
    #The below block of code flairs the gifter based on their current flair
    if gifterflair=="" or gifterflair is None:
        newgifterflair="Gifted :gifted:"
        gclass="d71c77b0-369d-11e1-967f-12313d096aae"
        
    elif "Gifted" in gifterflair:
        newgifterflair="No flair change"
    
    elif "Grabbed" in gifterflair:
        newgifterflair="Gifted :Gifted: | " + gifterflair
        gcountsearch=re.search(r"(?i)Grabbed (\d{0,3})", str(gifterflair))
        gcount=int(gcountsearch.group(1))
        if gcount is None or gcount == 0:
            newgifterflair="No flair change"
            print("Error for Gifter flair; no existingg grabbed count", gifter, giftee, comment)
        elif gcount <=6:
            gclass="4833a8ca-93c2-11e6-8e11-0e5c5e976c56"
        elif gcount <=10:
            gclass="77692912-93c2-11e6-a71e-0e69ab969334"
        elif gcount <=16:
            gclass="7b69d4b2-93c2-11e6-8fb2-0e0d983a7ee7"
        elif gcount < 30:
            gclass="c2dbae7e-93c2-11e6-a022-0e6883be649c"
        elif gcount > 29:
            gclass="c697b846-93c2-11e6-b133-0ebe89b429e6"
    
    if newgifterflair!="No flair change":
        GoG.flair.set(gifter,text=newgifterflair,flair_template_id=gclass)
        
#     print("Gifter " + gifter + "'s, new flair is " + newgifterflair + " with flair class " + gclass)

#     print(gifted, receiverflair)
    #The below block of code flairs the receiver based on their flair
    if receiverflair=="" or receiverflair is None:
        newreceiverflair="Grabbed 1 :Grabbed1-9:"
        rcount=0
        rclass="4833a8ca-93c2-11e6-8e11-0e5c5e976c56"
    elif receiverflair.replace(" ","")=="Gifted" or receiverflair.replace(" ","")=="Gifted:Gifted:":
        newreceiverflair= "Gifted :Gifted: | Grabbed 1"
        rclass="f95f90aa-369d-11e1-ab9b-12313d2c1af1"
        rcount=0
    
    elif "Gifted" in receiverflair and "Grabbed" in receiverflair:
        newreceiverflairsearch=re.search(r"(?i)Grabbed (\d{0,3})", str(receiverflair))
        rcount=int(newreceiverflairsearch.group(1))+1
        if rcount is None or rcount == 0:
            print("Error for Receiver flair; no grabbed count", gifter, giftee, comment)
            receiverflair=""
            return
        elif rcount <=9:
            rclass="f95f90aa-369d-11e1-ab9b-12313d2c1af1"
            remoji=":Grabbed1-9:"
        elif rcount <=19:
            rclass="6b1c5d7a-8fce-11e6-8b47-0e93c7828946"
            remoji=":Grabbed10-19:"
        elif rcount <=29:
            rclass="717f3a48-8fce-11e6-ba41-0ee844677561"
            remoji=":Grabbed20-29:"
        elif rcount > 29:
            rclass="13c64bc4-93a9-11e6-a5e6-0eda72ca337c"
            remoji=":Grabbed30andabove:"
        newreceiverflair="Gifted :Gifted:| Grabbed " + str(rcount) + remoji
            
    elif "Grabbed" in receiverflair:
        newreceiverflairsearch=re.search(r"(?i)Grabbed (\d{0,3})", str(receiverflair))
        rcount=int(newreceiverflairsearch.group(1))+1
        if rcount <6:
            rclass="4833a8ca-93c2-11e6-8e11-0e5c5e976c56"
        elif rcount <10:
            rclass="77692912-93c2-11e6-a71e-0e69ab969334"
        elif rcount <16:
            rclass="7b69d4b2-93c2-11e6-8fb2-0e0d983a7ee7"
        elif rcount < 30:
            rclass="c2dbae7e-93c2-11e6-a022-0e6883be649c"
        elif rcount > 29:
            rclass="c697b846-93c2-11e6-b133-0ebe89b429e6"
        newreceiverflair="Gifted :Gifted:| Grabbed " + str(rcount)
    
    elif "Cooldown" in receiverflair:
        Wiki = GoG.wiki["cooldownlog"]
        WikiContent = Wiki.content_md.strip()
        WikiContent = str(WikiContent).replace("\n\n\n","\n\n")
        for line in WikiContent.splitlines():
            if line is None:
                break
            if len(line) == 0: #if line is empty, skip
                #print('Empty line, skipping')
                continue
            if str(gifted).lower() in str(line).lower():
                print(str(line))
                FlairInfo = re.search(r"(?i)([\w-]*?) ((?:(Gifted) \| )?(?:(Grabbed) (\d{0,3}))?)(?: ?(?:emoji)?:[\w-]*:)? ?\|\| (.*) \|\| (\d*-\d*-\d*)", str(line))
                if FlairInfo is not None:
                    print('Found ' + gifted)
                    CooldownUser = FlairInfo.group(1)
                    CooldownDate = FlairInfo.group(7)
                    if FlairInfo.group(3) is not None:
                        GiftedFlair = FlairInfo.group(3) + " | "
                    else:
                        GiftedFlair = ""
                    GrabbedNum = int(FlairInfo.group(5).replace("+",""))+1
                    FlairCSS = FlairInfo.group(6)
                    print("Updating", str(gifted) + "'s", "flair while on cooldown")
                    newreceiverflair = str(GiftedFlair) + " Grabbed " + str(GrabbedNum)
                    UpdatedCooldownFlair = str(gifted) + " " + str(GiftedFlair) + "Grabbed " + str(GrabbedNum) + " || " + str(FlairCSS) + " || " + str(CooldownDate)
                    WikiContent = str(WikiContent).replace(line,UpdatedCooldownFlair).replace("\n\n\n","\n\n")
                    WikiUpdateReason = str("Updating " + gifted)
                    Wiki.edit(content=WikiContent, reason=WikiUpdateReason)
                    comment.reply(str(gifter) + " gifted " + str(gifted) + "who's new flair is " + str(newreceiverflair) + " but is currently on a cooldown.")
                else:
                    print(str(gifted) + " on cooldown but error occurred while updating")
                    # BUG: cooldown flair not properly updated. Unsure why - not finding the gift?
                    comment.reply(str(gifter) + " gifted " + str(gifted) + " but an error occurred while updating the receiver's flair. u/JpsCrazy please see above.")
                    return
            continue

    if newreceiverflair=="" or newreceiverflair is None:
        return
    if "Cooldown" not in receiverflair:
        GoG.flair.set(gifted,text=newreceiverflair,flair_template_id=rclass)
        print("Receiver " + gifted + "'s, new flair is " + newreceiverflair + " with flair class " + rclass)
        #Sort out flair classes for both the receiver and gifter

        comment.reply(str(gifter) + " gifted " + str(gifted) + " whose new flair is " + str(newreceiverflair))


def doCooldown(UserToCooldown, GoG):
    # BUG: should really pass reddit down instead of re-creating it
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
        GoG.flair.set(UserToCooldown, text='Cooldown', flair_template_id='fc209f40-4a53-11eb-91c6-0e5cd6fe1571')
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
                    # print("Putting", str(User), "on cooldown")
                    doCooldown(str(User), GoG)

def FlairAssigner(User, Giftee, comment, parent, GoG):
    ###--Assigns user flair from !gift commands
    LinkFlairText = parent.parent().link_flair_text
    if LinkFlairText=="REQUEST" or LinkFlairText=="CLOSED REQUEST":
        parent.parent().flair.select("a02ee300-3db4-11eb-9965-0e3501162567")
        doFlair(str(User),str(parent.parent().author), comment, GoG)
        ##NEEDED: enable cooldown on Requests, below
        ##doCooldown(parent.parent().author, GoG)
        
    elif LinkFlairText=="OFFER" or LinkFlairText=="CLOSED OFFER":
        doFlair(str(User),(str(Giftee)), comment, GoG)
        
    elif LinkFlairText=="GOG":
        if Giftee is not None:
            doFlair(str(User),str(Giftee), comment, GoG)
        else:
            if str(User).lower() == str(parent.parent().author).lower():
                comment.reply("It appears you attempted to gift yourself. Please double check your comment and try again. \n\nPlease [contact the moderators](https://www.reddit.com/message/compose?to=%2Fr%2FGiftofGames) if you believe this action was made in error.")
            else:
                doFlair(str(User),str(parent.parent().author), comment, GoG)
