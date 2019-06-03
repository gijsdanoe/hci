import tkinter as tk
from tkinter import ttk
import praw
from tkinter import simpledialog
import threading
from tkinter import messagebox
from tkinter import filedialog
import os

class ResponseTreeDisplay(tk.Frame):

    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)
        self.root = parent
        # Get Treeview
        self.tree = ttk.Treeview(self.root, columns='comment', show=('tree', 'headings'))
        # Get Heading: Comment
        self.tree.heading('comment', text='Comment')
        self.tree.column('comment', width=750, stretch='no')
        # Modify Tree
        self.tree.column('#0', width=150, stretch='no')
        # Get Vertical Scrollbar for Treeview
        sb = tk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        sb.place(x=942, y=200, height=225, anchor='center')
        # Place & Configure Treeview
        self.tree.place(relx=0.5, y=200, anchor='center')
        self.tree.configure(yscrollcommand=sb.set)
        # Set Id for Items
        self.id = 0
        self.count = 0
        self.url = None


    def get_url(self):
        dir = os.getcwd()
        filename = filedialog.askopenfilename(initialdir = dir,title = "Select file",filetypes = (("pickle files","*.pickle"),("all files","*.*")))
        return filename

    def conversation_queue(self, filename):
        conversation_list = []
        try:
            with open(filename, "rb") as f:
                while 1:
                    try:
                        conversation = filename.load(f)
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
                            self.tree.insert("", "0", connum, text=tweet)
                        if i > 0:
                            self.tree.insert(connum, "end", text=tweet)
                except:
                    pass
        except TypeError:
            pass



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
    menu2.add_command(label='Open', command=a.get_url)
    # Adds Menu2 to Menubar
    menubar.add_cascade(label='File', menu=menu2)
    # Adds Menubar to Root
    root.config(menu=menubar)
    root.mainloop()


if __name__ == '__main__':
    main()
