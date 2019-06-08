#!/usr/bin/python3
# Authors: G.Danoe (s3494888) & B.Kleppe (s3151522)
# Loads in a file, displays the tweets and allows the users to filter.
# Date: 08-06-2019

import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
import threading
from tkinter import *
from tkinter import messagebox
from tkinter import Scale
from tkinter import filedialog
from tkinter import HORIZONTAL
from tkinter import RIGHT
from tkinter import Button
from tkinter import Label
import os
import pickle
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class ResponseTreeDisplay(tk.Frame):

    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)
        self.root = parent
        # Get Treeview
        self.tree = ttk.Treeview(self.root)
        self.tree.column("#0", width=700)
        self.tree.heading('#0', text='Conversations')
        # Get Vertical Scrollbar for Treeview
        sb = tk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        sb.place(x=860, y=330, height=225, anchor='center')
        # Place & Configure Treeview
        self.tree.place(relx=0.5, y=450, anchor='s')
        self.tree.configure(yscrollcommand=sb.set)

        # Sentiment
        self.var = IntVar()
        self.var.set(0)
        self.emptylabel=Label(self.root,text=' ').grid(row=0,padx=75)
        self.sentiment_label = Label(self.root, text="Sentiment score").grid(row=0,column=1,sticky='w')
        self.b0 = Radiobutton(self.root, text="all", variable=self.var, value=0).grid(row=1, column=1, sticky='w')
        self.b1 = Radiobutton(self.root, text="positive", variable=self.var, value=1).grid(row=2,column=1, sticky='w')
        self.b2 = Radiobutton(self.root, text="neutral", variable=self.var, value=2).grid(row=3,column=1,sticky='w')
        self.b3 = Radiobutton(self.root, text="negative", variable=self.var, value=3).grid(row=4,column=1,sticky='w', pady=20)

        # Length
        self.min_c = Label(self.root, text="Min").grid(row=1,column=2,padx=15)
        self.max_c = Label(self.root, text="Max").grid(row=2,column=2,padx=15)
        self.con_label = Label(self.root, text="Length of conversation").grid(row=0,column=3)
        self.min_con = Scale(self.root, from_=3, to=10, tickinterval=3, orient=HORIZONTAL)
        self.min_con.set(2)
        self.max_con = Scale(self.root, from_=3, to=10, tickinterval=3, orient=HORIZONTAL)
        self.max_con.set(10)
        self.min_con.grid(row=1, column=3)
        self.max_con.grid(row=2, column=3)

        # Unique users
        self.min_u = Label(self.root, text="Min").grid(row=1,column=4,padx=15)
        self.max_u = Label(self.root, text="Max").grid(row=2,column=4,padx=15)
        self.usr_label = Label(self.root, text="Number of unique users").grid(row=0,column=5)
        self.min_usr = Scale(self.root, from_=2, to=10, tickinterval=3, orient=HORIZONTAL)
        self.min_usr.set(2)
        self.max_usr = Scale(self.root, from_=2, to=10, tickinterval=3, orient=HORIZONTAL)
        self.max_usr.set(10)
        self.b = Button(self.root, text='Filter', command=self.filteredall)
        self.min_usr.grid(row=1, column=5)
        self.max_usr.grid(row=2, column=5)
        
        self.b.grid(row=1, column=6,padx=30)
        self.conversation_list = []
        self.con_length = []
        self.unique_usr = []
        self.filename = ''


    # allows you to open a file
    def getfile(self):
        dir = os.getcwd()
        self.filename = filedialog.askopenfilename(initialdir = dir,title = "Select file",filetypes = (("pickle files","*.pickle"),("all files","*.*")))

    # puts the conversations, the unique users and the length in lists
    def conversation_queue(self, filename):
        try:
            with open(filename, "rb") as f:
                while 1:
                    try:
                        conversation = pickle.load(f)
                        self.conversation_list.append(conversation[0])
                        self.con_length.append(conversation[1])
                        self.unique_usr.append(conversation[2])
                    except EOFError:
                        break
        except FileNotFoundError:
            pass

    # puts the conversations in the treeview
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
                            self.tree.insert("", "0", connum, text=tweet)
                        if i > 0:
                            self.tree.insert(connum, "end", text=tweet)
                except:
                    pass
        except TypeError:
            pass

    # runs all functions
    def all(self):
        self.getfile()
        self.conversation_queue(self.filename)
        self.show_convo(self.conversation_list)

    # runs functions with filters
    def filteredall(self):

        #for all conversations we compare the average sentiment scores with the sentiment score of the first tweet, so we can determine whether a conversation gets positive, negative or stays neutral

        analyser = SentimentIntensityAnalyzer()
        sentdictlist = []
        for i in self.conversation_list:
            sentdict = {}
            for j in i:
                sentdict[j] = analyser.polarity_scores(j)['compound']
            sentdictlist.append(sentdict)

        sentdictlistdict = {}
        for i,sentdict in enumerate(sentdictlist):
            valuelist = []
            for key, value in sentdict.items():
                valuelist.append(value)

            avgvalue = sum(valuelist) / len(valuelist)

            if valuelist[0]-avgvalue <= 0.1 and valuelist[0]-avgvalue >= -0.1:
                sentdictlistdict[i] = 2
            elif valuelist[0] <= avgvalue:
                sentdictlistdict[i] = 1
            elif valuelist[0] >= avgvalue:
                sentdictlistdict[i] = 3

        # allows the user to filter using widgets, on sentiment but also on unique users and length
        newconvolist = []
        for i, (key, value) in enumerate(sentdictlistdict.items()):
            if value == self.var.get() or self.var.get() == 0:
                if self.con_length[i] <= self.max_con.get() and self.con_length[i] >= self.min_con.get():
                    if self.unique_usr[i] <= self.max_usr.get() and self.unique_usr[i] >= self.min_usr.get():
                        for j, item in enumerate(self.conversation_list):
                            if i == j:
                                newconvolist.append(item)
        self.show_convo(newconvolist)



def main():
    root = tk.Tk()
    # Set Root
    root.geometry('1000x500')
    root.resizable(width=0, height=0)
    root.title('Part 2')
    a = ResponseTreeDisplay(root)
    # Creates Menubar
    menubar = tk.Menu(root)
    # Creates Menu 'File' with Items 'Open' and 'Exit'
    menu2 = tk.Menu(menubar, tearoff=0)
    menu2.add_command(label='Open', command=a.all)
    menu2.add_command(label="Exit", command=root.quit)
    # Adds Menu2 to Menubar
    menubar.add_cascade(label='File', menu=menu2)
    # Adds Menubar to Root
    root.config(menu=menubar)

    root.mainloop()

if __name__ == '__main__':
    main()
