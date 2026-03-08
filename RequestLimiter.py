import datetime
import time

import traceback
import math

#local
import Remover

ThreeDays = 86400*3 #86400 seconds is 1 day

def RepostCheck(reddit, User, SubmissionDate, PostID, RequestOrComment="Request"):
    try:
        ###--Removes post if Request exists that's <3 days old
        UserPostHistory = reddit.redditor("{}".format(User)).submissions.new()
        for post in UserPostHistory:
            if post is None:
                #print("End of posts")
                break
            if post.banned_by!=None:
                #print("Post already moderated", post.title)
                continue
            if PostID == post.id:
                #print("Skipping subject post for search")
                continue

            FoundSubmissionDate = post.created_utc

            if FoundSubmissionDate > SubmissionDate:
                #print("Post newer than subject post", post.title, FoundSubmissionDate, SubmissionDate)
                continue
            
            if "giftofgames"!=str(post.subreddit).lower():
                #print("Unrelated post", post.title)
                continue
            if "[request]" in str(post.title).lower():
                TimeDifference = SubmissionDate - FoundSubmissionDate
                #print(post.title, TimeDifference, ThreeDays)
                
                if TimeDifference < ThreeDays:
                    RequestTimeCheckDaysMinutes = round((TimeDifference / 60))
                    RequestTimeCheckDaysHours = math.floor((RequestTimeCheckDaysMinutes / 60))
                    RequestTimeCheckDaysMinutes -= RequestTimeCheckDaysHours*60
                    RequestTime = str((str(RequestTimeCheckDaysHours) + " hours and " + str(RequestTimeCheckDaysMinutes) + " minutes old."))
                    print(User, "new Request removed as prior is", RequestTime, post.id)                    
                    RemovalReason = "Request Limit"
                    Remover.GeneralRemove(RequestOrComment, PostID, RemovalReason, RequestTime)


            #Calc difference between requests
            #If there is <72 hours between Requests
            #Calc difference between now and older request
            #If still too early, tell them time left
            #If able to post, say so
            
#             FoundSubmissionDate = post.created_utc
#             if FoundSubmissionDate > SubmissionDate:
#                 RemovingPostID = post.id
#                 RemovingPostAge = post.created_utc
#                 OldPostAge = SubmissionDate
#                 TimeDifference = FoundSubmissionDate-SubmissionDate
#             else:
#                 RemovingPostID = PostID
#                 RemovingPostAge = SubmissionDate
#                 OldPostAge = post.created_utc
#                 TimeDifference = SubmissionDate-FoundSubmissionDate
#             if TimeDifference >= ThreeDays:
#                 break
#             PostAge = time.time()-RemovingPostAge
            
#             if PostAge >= ThreeDays:
#                 print("Post should be removed but is already >3 days old at time of review ", RemovingPostID)
#                 break


#             if "[request]" in str(post.title).lower() and "giftofgames"==str(post.subreddit).lower():
#                 RequestTimeCheckDaysMinutes = round((PostAge / 60))
#                 RequestTimeCheckDaysHours = math.floor((RequestTimeCheckDaysMinutes / 60))
#                 RequestTimeCheckDaysMinutes -= RequestTimeCheckDaysHours*60
#                 RequestTime = str((str(RequestTimeCheckDaysHours) + " hours and " + str(RequestTimeCheckDaysMinutes) + " minutes old."))
#                 print(User, "posted new Request while last post is", RequestTime, "Removing post.", RemovingPostID)                    
#                 RemovalReason = "Request Limit"
# #                 Remover.GeneralRemove(RequestOrComment, RemovingPostID, RemovalReason, RequestTime)

    except Exception as e:
        print("RepostCheck", e, traceback.format_exc())

def PCTagCheck(User, Title, PostID, GoG, RequestOrComment="Request"):
    word_list = GoG.wiki['index/oro-ignored-words'].content_md.strip().replace('"','').replace("[","").replace("]","").replace(", ",",").split(",")
    try:
        ###--Checks if user is using [PC] tag for approved games
        ExcludedPost = False
        if "[pc]" not in str(Title).lower():
            return
            
        for word in word_list:
            if word.lower() in str(Title).lower():
                ExcludedPost = True
##              print("User using [PC] tag correctly")
                break
            
        if ExcludedPost == False:
            print(str(User), "used [PC] tag incorrectly; removing post")
            RemovalReason = "[PC] tag used incorrectly"
            Remover.GeneralRemove(RequestOrComment, PostID, RemovalReason)

    except Exception as e:
        print("PCTagCheck", e, traceback.format_exc())
