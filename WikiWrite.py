import traceback

def WriteWiki(WikiPage, WikiLine, GoG):
    try:
        Wiki = GoG.wiki[WikiPage]
        if WikiLine not in str(Wiki.content_md):
            # if "https://reddit.com/" not in WikiLine:
                # print(WikiLine)
            UpdatedLog = str(str(Wiki.content_md) + "\n\n" + WikiLine)
            WikiUpdateReason = str(WikiLine)
            Wiki.edit(content=UpdatedLog, reason=WikiUpdateReason)
            
    except Exception as e:
        print("WriteWiki", e, traceback.format_exc())
