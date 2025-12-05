import traceback
import praw

reddit = praw.Reddit('GOGUserHistoryBot', user_agent='GOGUserHistoryBot_3.1')
GoG = reddit.subreddit("GiftofGames")

def GeneralRemove(RequestOrComment, PostID, RemovalReason, RequestTime="Error"):
    try:
        if RequestOrComment == "Request":
            PostID = reddit.submission("{}".format(PostID))
            PublicOrPrivate = "public"
        elif RequestOrComment == "Comment":
            PostID = reddit.comment("{}".format(PostID))
            PublicOrPrivate = "private_exposed"
        global RemovalMessage
        RemovalMessageOpening = "**Your " + RequestOrComment + " has been removed**. Please read our [full rules](https://www.reddit.com/r/GiftofGames/wiki/rules).\n\n**Reason**: "
        RemovalMessageEnding = "\n\nThis action was automatically performed by a bot. Please [contact the moderators](https://www.reddit.com/message/compose?to=%2Fr%2FGiftofGames) if you believe this action was made in error."
        if RemovalReason == None:
            print("SOMETHING IS TERRIBLY WRONG WITH REMOVAL REASONS. ABORTED REMOVAL.", PostID)
            exit()
        if RemovalReason == "Karma":
            RemovalReasonText = "FreeKarma user; " + RequestOrComment
            RemovalMessage = RemovalMessageOpening + "You have less than 300 comment karma when accounting for karma from subreddits such as r/FreeKarma4U. Please gain karma naturally and try again." + RemovalMessageEnding
        elif RemovalReason == "GiveawayUsage":
            RemovalReasonText = "High giveaway sub usage; " + RequestOrComment
            RemovalMessage = RemovalMessageOpening + "A significant portion of your recent Reddit history consists of posting on giveaway subs. Please diversify your posting habits and try again." + RemovalMessageEnding
        elif RemovalReason == "Alt":
            RemovalReasonText = "Alt usage detected; " + RequestOrComment
            RemovalMessage = RemovalMessageOpening + "It appears you have previously used a different Steam ID on this subreddit. Only one account for each platform may be used on this subreddit." + RemovalMessageEnding
        elif RemovalReason == "Low Steam Level":
            RemovalReasonText = "Low Steam level detected; " + RequestOrComment
            RemovalMessage = RemovalMessageOpening + "Your Steam account must be at least level 2 (a/k/a no [limited user accounts](https://support.steampowered.com/kb_article.php?ref=3330-iagk-7663))." + RemovalMessageEnding
        elif RemovalReason == "Low Steam Level 0":
            RemovalReasonText = "Low Steam level detected - NULL; " + RequestOrComment
            RemovalMessage = RemovalMessageOpening + "Your Steam account must be at least level 2 (a/k/a no [limited user accounts](https://support.steampowered.com/kb_article.php?ref=3330-iagk-7663))." + RemovalMessageEnding
        elif RemovalReason == "Private Steam Profile":
            RemovalReasonText = "Private Steam profile detected; " + RequestOrComment
            RemovalMessage = RemovalMessageOpening + "Your Steam profile must be set to public. [Click here](https://i.imgur.com/yktxqoQ.gifv) to see how." + RemovalMessageEnding
        elif RemovalReason == "Private Steam Library":
            RemovalReasonText = "Private Steam library detected; " + RequestOrComment
            RemovalMessage = RemovalMessageOpening + "Your Steam library must be set to public. [Click here](https://i.imgur.com/yktxqoQ.gifv) to see how." + RemovalMessageEnding
        elif RemovalReason == "[PC] tag used incorrectly":
            RemovalReasonText = "[PC] tag used incorrectly; " + RequestOrComment
            RemovalMessage = RemovalMessageOpening + "[PC] is the incorrect tag for the request you are making. [Click here](https://www.reddit.com/r/GiftofGames/wiki/rules#wiki_2.1.29_include_the_relevant_platform_in_the_title_.28i.e._.5Boffer.5D.5Bsteam.5D.2C_.5Brequest.5D.5Bps4.5D.29) for the relevant section of the rules." + RemovalMessageEnding
        elif RemovalReason == "Request Limit":
            RemovalReasonText = "Request posted within 3 days of another Request; " + RequestOrComment
            RemovalMessage = RemovalMessageOpening + "You may only post one Request every 72 hours (3 days). Your last Request was is " + str(RequestTime) + " Reddit may round the time of your last post making it appear older than it actually is." + RemovalMessageEnding
        # print(RemovalReasonText)
        PostID.mod.remove(mod_note=RemovalReasonText)
        PostID.mod.send_removal_message(RemovalMessage, title=RemovalReason, type=PublicOrPrivate)
        RemovalReason = None

    except Exception as e:
        print("GeneralRemove", e, traceback.format_exc())

    ##def KarmaRequestThreshholdRemove():
    ##    reddit.submission("{}".format(RequestID)).mod.remove(mod_note="FreeKarma user; Request")
    ##    reddit.submission("{}".format(RequestID)).mod.send_removal_message("**Your Request has been removed**. Please read our [full rules](https://www.reddit.com/r/GiftofGames/wiki/rules).\n\n**Reason**: Too much of your comment karma is from subreddits such as r/FreeKarma4U. Please gain karma naturally and try again.  \n\nThis action was automatically performed by a bot. Please [contact the moderators](https://www.reddit.com/message/compose?to=%2Fr%2FGiftofGames) if you believe this action was made in error.", type='public')
    ##
    ##def KarmaCommentThreshholdRemove():
    ##    reddit.comment("{}".format(OfferCommentID)).mod.remove(mod_note="FreeKarma user; Offer comment")
    ##    reddit.comment("{}".format(OfferCommentID)).mod.send_removal_message("Please read our [full rules](https://www.reddit.com/r/GiftofGames/wiki/rules).\n\n**Reason**: Too much of your comment karma is from subreddits such as r/FreeKarma4U. Please obtain karma naturally and try again.  \n\nThis action was automatically performed by a bot. Please respond to this message if you believe this action was made in error.", title='Your comment on r/GiftofGames has been removed', type='private_exposed')
