import traceback
import re

def WriteWiki(WikiPage, WikiLine, GoG):
    try:
        Wiki = GoG.wiki[WikiPage]
        WikiLine = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', str(WikiLine)).encode('utf-8', errors='ignore').decode('utf-8')
        if WikiLine not in str(Wiki.content_md):
            # if "https://reddit.com/" not in WikiLine:
                # print(WikiLine)
            UpdatedLog = str(re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', str(Wiki.content_md)).encode('utf-8', errors='ignore').decode('utf-8') + "\n\n" + WikiLine)
            WikiUpdateReason = str(WikiLine)
            Wiki.edit(content=UpdatedLog, reason=WikiUpdateReason)
            
    except Exception as e:
        print("WriteWiki", e, traceback.format_exc())
