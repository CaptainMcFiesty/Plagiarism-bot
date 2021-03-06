import praw
import OAuth2Util
import time

plag_names = []
INTERVAL = 30 #minutes
running = True
subname = 'photoshopbattles'

r = praw.Reddit("Plagiarism control by /u/Captain_McFiesty ver 0.4")
o = OAuth2Util.OAuth2Util(r)

subreddit = r.get_subreddit(subname)


def check_comments(top):
    for comment in top:
        if(comment.author != None):
            for comment2 in top:
                if(comment2.author != None):
                    #print(comment2.author)
                    if (comment2.body == comment.body and
                            comment.author.name != comment2.author.name and
                            comment2.id != comment.id):
                        if (comment2.created > comment.created and
                               comment2.author.name not in plag_names):
                            print('Plagiarism, id = %r, user = %r'
                                      % (comment2.id, comment2.author.name))
                            plag_names.append(comment2.author.name)
                            #comment2.report('Bot report: Plagiarism suspected')
                            subreddit.add_ban(comment2.author.name)
                            comment2.remove(spam=False)
    return

def filter_comments(flat_comments):
    top_level = []
    for comment in flat_comments:
        if (comment.is_root and comment.banned_by == None):
            top_level.append(comment)
    #print_list(top_level)
    return top_level

def print_list(top):
    print('\nTop Level List')
    for c in top:
        print(c.id)
        print(c.author)
    print('\n')
    return

def add_to_wiki():
    wiki = r.get_wiki_page(subname,'plagnames')
    if (wiki.content_md == ''):
        text = 'Plagiarism users  \n'
    else:
        text = wiki.content_md
    if(plag_names != []):
        for user in plag_names:
            text += '/u/'+user+'  \n'
        plag_names.clear()
        wiki.edit(text, 'Added plagiarism users')
    return

def do_code():
    for submission in subreddit.get_hot(limit=5):
        if submission.num_comments > 100:
            print('Submission id: %r' % submission.id)
            submission.replace_more_comments(limit=None, threshold=0)
            flat_comments = praw.helpers.flatten_tree(submission.comments)
            top_level = filter_comments(flat_comments)
            check_comments(top_level)
            # print_list(top_level)
    add_to_wiki()
    return

def accept_invite():
    for message in r.get_unread():
    #for message in r.get_messages():
            if(message.body.startswith('**gadzooks!')):
                sub = r.get_info(thing_id=message.subreddit.fullname)
                if(message.subreddit.display_name == subname):
                    try:
                        sub.accept_moderator_invite()
                    except(praw.errors.InvalidInvite):
                        continue
                    message.mark_as_read()
    return

#accept_invite()
#do_code()

while running:
    o.refresh()
    print("Local time: ", time.asctime(time.localtime(time.time())))
    try:
        #accept_invite()
        do_code()
    except KeyboardInterrupt:
        running = False
    except (praw.errors.APIException):
        print("[ERROR]:")
        print("sleeping 30 sec")
        sleep(30)
    except (praw.errors.HTTPException):
        print("Connection Error")
        time.sleep(INTERVAL/2*60)
    except (praw.errors.PRAWException):
        print("PRAW Error")
        time.sleep(INTERVAL/2*60)
        continue
    except (Exception):
        print("[ERROR]:")
        print("blindly handling error")
        break
    time.sleep(INTERVAL*60)
