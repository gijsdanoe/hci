# Authors: G.Danoe & B.Kleppe
# Downloads a Twitter stream, customizable search options and analyses the conversations.
# Date: 03-04-2019

import tweepy
import json
import queue
import threading
import pickle
from tweepy import Stream
from tweepy.streaming import StreamListener

# Import credentials from text file
def import_credentials(txt):
    with open(txt,'r') as f:
        credentials = eval(f.read())
    return credentials

# Check the replies
def check_reply(q1_reply_id, list_replies):
    try:
        reply_list = list_replies
        reply = api.get_status(q1_reply_id)
        text = reply.text
        reply_list.append(text)
        new_id = reply.in_reply_to_status_id
        if new_id != None:
            check_reply(new_id, reply_list)
        else:
            pass
        return reply_list[::-1]
    except tweepy.error.TweepError:
        return ["This Twitter conversation is private"]

# Go to next conversation
def next_conversation():
    q1 = q.get()
    q1_reply = q1['in_reply_to_status_id']
    return check_reply(q1_reply, [q1['text']])

def setQueue():
    with open('text1.txt', 'r') as output:
        for line in output:
            try:
                newline = json.loads(line)
                if newline['in_reply_to_status_id']:
                    q.put(newline)
            except KeyError:
                pass

def save(conversation, file):
    if 3 <= len(conversation) <= 10:
        with open(file, "ab") as f:
            pickle.dump(conversation, f)
    else:
        pass

def get_conversations(file):
    conversation_list = []
    with open(file, "rb") as f:
        while 1:
            try:
                conversation = pickle.load(f)
            except EOFError:
                break
            conversation_list.append(conversation)
    return conversation_list

# Setting the credentials
credentials = import_credentials('credentials.txt')
API_key = credentials['app_key']
API_secret = credentials['app_secret']
OAUTH_token = credentials['oauth_token']
OAUTH_token_secret = credentials['oauth_token_secret']

# Basic listener, prints the stream to std output
class Listener(StreamListener):
    def __init__(self, queue):
        super(Listener, self).__init__()
        self.queue = queue
    
    def on_data(self, data):
        with open('text1.txt', 'a') as output:
            output.write(data)
        return True

    def on_error(self, status):
        print(status)


if __name__ == '__main__':
    q = queue.Queue()
    listener = Listener(q)
    auth = tweepy.OAuthHandler(API_key, API_secret)
    auth.set_access_token(OAUTH_token, OAUTH_token_secret)
    api = tweepy.API(auth)
    stream = Stream(auth, listener)
    stream.filter(track=["why"],languages=['en'], async=True)
    setQueue()

    
    while True:
        threading.Thread(target=save, args=([next_conversation()], "text.pickle"), daemon=True).start()
        x = get_conversations('text.pickle')
        print(x)
    '''with open("text.pickle", "rb") as f:
        for i in range(10):
            print(pickle.load(f))

'''
# EXCEPT PICKLE OUTPUT ERR: EOFError:

    #with open('output.pickle', 'rb') as output:
    #   itemlist = pickle.load(output)
        
