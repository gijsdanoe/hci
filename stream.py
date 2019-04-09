# Authors: G.Danoe & B.Kleppe
# Downloads a Twitter stream, customizable search options and analyses the conversations.
# Date: 03-04-2019

import sys
import tweepy
import json
import queue
import threading
import pickle
import time
from tweepy import Stream
from tweepy.streaming import StreamListener

# Import credentials from text file
def import_credentials(txt):
    with open(txt,'r') as f:
        credentials = eval(f.read())
    return credentials

# Setting the credentials
credentials = import_credentials('credentials.txt')
API_key = credentials['app_key']
API_secret = credentials['app_secret']
OAUTH_token = credentials['oauth_token']
OAUTH_token_secret = credentials['oauth_token_secret']

class RawConversations():

    def __init__(self, queue, queue2, listener):
        self.queue = q
        self.queue2 = q2
        self.listener = listener

        self.setQueue()

        self.auth = tweepy.OAuthHandler(API_key, API_secret)
        self.auth.set_access_token(OAUTH_token, OAUTH_token_secret)
        self.api = tweepy.API(self.auth)
        self.stream = Stream(self.auth, listener)
        self.stream.filter(track=["why"],languages=['en'], async=True)
            
        self.thread = threading.Thread(target=self.run, daemon=True).start()
        self.thread2 = threading.Thread(target=self.conversation_queue, daemon=True).start()

    def run(self):
        while True:
            self.save(self.next_conversation())

    # Go to next conversation
    def next_conversation(self):
        q1 = self.queue.get()
        q1_reply = q1['in_reply_to_status_id']
        return self.check_reply(q1_reply, [q1['text']])

    # Check the replies
    def check_reply(self, q1_reply_id, list_replies):
        try:
            reply_list = list_replies
            reply = self.api.get_status(q1_reply_id)
            text = reply.text
            reply_list.append(text)
            new_id = reply.in_reply_to_status_id
            if new_id != None:
                self.check_reply(new_id, reply_list)
            else:
                pass
            return reply_list[::-1]
        except tweepy.error.TweepError:
            return ["This Twitter conversation is private"]

    def setQueue(self):
        try:
            with open('text1.txt', 'r') as output:
                for line in output:
                    try:
                        newline = json.loads(line)
                        if newline['in_reply_to_status_id']:
                            self.queue.put(newline)
                    except KeyError:
                        pass
        except FileNotFoundError:
            pass

    def save(self, conversation):
        if 3 <= len(conversation) <= 10:
            with open("text.pickle", "ab") as f:
                pickle.dump(conversation, f)
        else:
            pass


    def conversation_queue(self):
        conversation_list = []
        try:
            with open("text.pickle", "rb") as f:
                while 1:
                    try:
                        conversation = pickle.load(f)
                        self.queue2.put(conversation)
                    except EOFError:
                        break
        except FileNotFoundError:
            self.save(self.next_conversation())



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
    q2 = queue.Queue()
    listener = Listener(q)
    x=RawConversations(q, q2, listener)
    

    while True:
        inp=input('type something to receive a chat')
        if inp:
            if q.empty():
                print("One second, still loading the comments, please try again in a few seconds")
                x.setQueue()
            elif q2.empty():
                x.save(x.next_conversation())
                x.conversation_queue()
            else:
                print(q2.get())


# EXCEPT PICKLE OUTPUT ERR: EOFError:

    #with open('output.pickle', 'rb') as output:
    #   itemlist = pickle.load(output)
        
