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
from tkinter import *
from tkinter import ttk

from threading import Timer
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

class RawConversations(Frame):

    def __init__(self, queue, listener, parent):
        self.queue = q
        self.listener = listener

        self.setQueue()

        self.auth = tweepy.OAuthHandler(API_key, API_secret)
        self.auth.set_access_token(OAUTH_token, OAUTH_token_secret)
        self.api = tweepy.API(self.auth)
        self.stream = Stream(self.auth, listener)
        self.stream.filter(track=["gargano"],languages=['en'], is_async=True)
            
        self.thread = threading.Thread(target=self.run, daemon=True).start()
        self.thread2 = threading.Thread(target=self.conversation_queue, daemon=True).start()

        Frame.__init__(self, parent)
        self.parent = parent
        self.tree = ttk.Treeview(self.parent)
        self.tree.column("#0", width = 700)
        self.tree.pack()

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
                    except:
                        pass
        except FileNotFoundError:
            pass

    def save(self, conversation):
        try:
            if 3 <= len(conversation) <= 10:
                with open("text.pickle", "ab") as f:
                    pickle.dump(conversation, f)
            else:
                pass
        except FileNotFoundError:
            pass


    def conversation_queue(self):
        conversation_list = []
        try:
            with open("text.pickle", "rb") as f:
                while 1:
                    try:
                        conversation = pickle.load(f)
                        conversation_list.append(conversation)
                    except EOFError:
                        break
            return conversation_list
        except FileNotFoundError:
            time.sleep(4)


    def show_convo(self, conversation_list):
        for connum, con in enumerate(conversation_list):
            for i, tweet in enumerate(con):
                try:
                    if i == 0:
                        self.tree.insert("","end",connum,text=tweet)
                    else:
                        self.tree.insert(connum, "end", text=tweet)
                except:
                    pass


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

def main():
    # Interface
    root = Tk()
    root.title("Comment Tree Display")
    root.geometry("800x600")
    root.option_add("*tearOff", False)

    # Menu bar
    menubar = Menu(root)
    comment_tree = RawConversations(root, listener, parent=None)
    convo = comment_tree.show_convo(comment_tree.conversation_queue())
    # File menu
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)

    # Processing menu
    procmenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Processing", menu=procmenu)

    root.config(menu=menubar)
    root.mainloop()
    print(comment_tree.conversation_queue()[0])


if __name__ == '__main__':
    q = queue.Queue()
    listener = Listener(q)
    main()

# EXCEPT PICKLE OUTPUT ERR: EOFError:

    #with open('output.pickle', 'rb') as output:
    #   itemlist = pickle.load(output)
        
