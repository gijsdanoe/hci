import tkinter as tk
from tkinter import ttk
import praw
from tkinter import simpledialog
import threading
from tkinter import messagebox
from tkinter import Scale
from tkinter import filedialog
from tkinter import HORIZONTAL
from tkinter import Button
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
        sb.place(x=942, y=200, height=225, anchor='center')
        # Place & Configure Treeview
        self.tree.place(relx=0.5, y=200, anchor='center')
        self.tree.configure(yscrollcommand=sb.set)
        self.w = Scale(self.root, from_=0, to=1, resolution=0.1, tickinterval=0.5, orient=HORIZONTAL)
        self.w.pack()
        self.conversation_list = []
        self.filename = ''

    def get_url(self):
        dir = os.getcwd()
        self.filename = filedialog.askopenfilename(initialdir = dir,title = "Select file",filetypes = (("pickle files","*.pickle"),("all files","*.*")))

    def conversation_queue(self, filename):
        try:
            with open(filename, "rb") as f:
                while 1:
                    try:
                        conversation = pickle.load(f)
                        self.conversation_list.append(conversation)
                    except EOFError:
                        break
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
                            self.tree.insert("", "0", connum, text=tweet)
                        if i > 0:
                            self.tree.insert(connum, "end", text=tweet)
                except:
                    pass
        except TypeError:
            pass

    def all(self):
        self.get_url()
        self.conversation_queue(self.filename)
        self.show_convo(self.conversation_list)
        print(self.w.get())

    def filteredall(self):

        analyser = SentimentIntensityAnalyzer()
        sentdictlist = []
        for i in self.conversation_list:
            sentdict = {}
            for j in i:
                sentdict[j] = analyser.polarity_scores(j)['compound']
            sentdictlist.append(sentdict)
        print(sentdictlist)

        for sentdict in sentdictlist:
            valuelist = []
            for key, value in sentdict.items():
                valuelist.append(value)

            print(sum(valuelist)/len(valuelist))
            for key,value in sentdict.items():
                if value < self.w.get():
                    for item in self.conversation_list:
                        if key in item:
                            self.conversation_list.remove(item)


        self.show_convo(self.conversation_list)



def main():
    root = tk.Tk()
    # Set Root
    root.geometry('1000x350')
    root.resizable(width=0, height=0)
    root.title('Part 2')
    a = ResponseTreeDisplay(root)
    # Creates Menubar
    menubar = tk.Menu(root)
    # Creates Menu 'File' with Item 'Exit'
    menu2 = tk.Menu(menubar, tearoff=0)
    menu2.add_command(label='Open', command=a.all)
    # Adds Menu2 to Menubar
    menubar.add_cascade(label='File', menu=menu2)
    b = Button(root, text='Filter', command=a.filteredall)
    b.pack()
    # Adds Menubar to Root
    root.config(menu=menubar)

    root.mainloop()

if __name__ == '__main__':
    main()
