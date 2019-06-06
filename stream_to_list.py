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
import geopy
import os
from geopy.geocoders import Nominatim
from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
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
        super(RawConversations, self).__init__()
        self.queue = q
        self.listener = listener
        self.filter = False
        self.filters = ""

        self.setQueue()

        self.auth = tweepy.OAuthHandler(API_key, API_secret)
        self.auth.set_access_token(OAUTH_token, OAUTH_token_secret)
        self.api = tweepy.API(self.auth)
            
        self.thread = threading.Thread(target=self.run, daemon=True).start()
        self.thread2 = threading.Thread(target=self.conversation_queue, daemon=True).start()

        Frame.__init__(self, parent)
        self.parent = parent
        self.tree = ttk.Treeview(self.parent)
        self.tree.column("#0", width = 700)
        self.tree.pack()
        self.text_var = StringVar()
        #self.loc_button = Button(self.parent, text="Location", command=self.location)
        self.status_label = Label(self.parent, textvariable=self.text_var).pack()
        self.text_var.set("Click on update in order to receive conversations")
        self.pause_button = Button(self.parent, text="Update", command=self.update).pack()


    def ask_filter(self):
        word=simpledialog.askstring("Input", "What word are you looking for?")
        lang=simpledialog.askstring("Input", "What language do you want?")
        self.stream = Stream(self.auth, listener)
        self.stream.filter(track=[word],languages=[lang], async=True)
        self.filter = True
        self.filters += word + lang
        self.text_var.set("Buffering, please wait a few seconds and update the tree...")
        #self.loc_button.pack()

        '''
    def location(self):
        self.stream.disconnect()
        location=simpledialog.askstring("Input", "Type in a city/country?")
        radius=simpledialog.askstring("Input", "What is the radius of your location in kilometres?")
        geolocator = Nominatim(user_agent="HCI_analyzer")
        geo_location = geolocator.geocode(location)
        coords = '{0},{1},{2}km'.format(geo_location.latitude, geo_location.longitude,radius)
        word=simpledialog.askstring("Input", "What word are you looking for?")
        language=simpledialog.askstring("Input", "What language do you want?")
        with self.queue.mutex:
            q.queue.clear()
        for status in tweepy.Cursor(self.api.search,q=word, lang=language, geocode=coords).items(10):
            with open('text2.txt', 'a') as output:
                output.write(str(status._json))
        self.setQueue2()
        self.update()
        '''
            
        
    
    def run(self):
        while True:
           self.save(self.next_conversation())


    def update(self):
        if self.filter == True:
            self.show_convo(self.conversation_queue())
            self.text_var.set("Click on update to receive more conversations")
        else:
            self.ask_filter()


    def file_streamer(self):
        try:
            if q.empty():
                self.setQueue()
            self.update()
        except:
            self.tree.insert("", "0", text="Not enough tweets available...")
            pass

        
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

    '''
    def setQueue2(self):
        try:
            with open('text2.txt', 'r') as output:
                for line in output:
                    try:
                        newline = json.loads(line)
                        if newline['in_reply_to_status_id']:
                            self.queue.put(newline)
                    except:
                        pass
        except FileNotFoundError:
            pass
    '''


    def save(self, conversation):
        if 3 <= len(conversation) <= 10:
            if self.filters != "":
                with open(self.filters+'.pickle', "ab") as f:
                    pickle.dump(conversation, f)
            else:
                pass
        else:
            self.save(self.next_conversation())


    def conversation_queue(self):
        conversation_list = []
        try:
            with open(self.filters+".pickle", "rb") as f:
                while 1:
                    try:
                        conversation = pickle.load(f)
                        conversation_list.append(conversation)
                    except EOFError:
                        break
                return conversation_list
        except FileNotFoundError:
            pass


    def show_convo(self, conversation_list):
        try:
            for i in self.tree.get_children():
                self.tree.delete(i)
            for connum, con in enumerate(conversation_list):
                try:
                    for i, tweet in enumerate(con):
                        if connum == 0:
                            pass
                        if i == 0 and connum >= 1:
                            self.tree.insert("","0",connum,text=tweet)
                        if i > 0:
                            self.tree.insert(connum, "end",text=tweet)
                except:
                    pass
        except TypeError:
            self.file_streamer()


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
    comment_tree = RawConversations(root, listener, root)
    #convo = comment_tree.show_convo(comment_tree.conversation_queue())
    # File menu
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)

    # Processing menu
    procmenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Processing", menu=procmenu)

    root.config(menu=menubar)
    root.mainloop()


if __name__ == '__main__':
    path = os.getcwd()
    for item in os.listdir(path):
        if item.endswith(".pickle"):
            os.remove(item)
    try:
        os.remove("text1.txt")
    except FileNotFoundError:
        pass
    q = queue.Queue()
    listener = Listener(q)
    main()


# EXCEPT PICKLE OUTPUT ERR: EOFError:

    #with open('output.pickle', 'rb') as output:
    #   itemlist = pickle.load(output)
        
