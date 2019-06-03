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
        filedialog.asksaveasfilename(initialdir = dir,title = "Select file",filetypes = (("pickle files","*.pickle"),("all files","*.*")))

    def show_comments(self, url):
        # Sends all Comments to add_to_tree Function
        self.clear_tree()
        self.url = url
        submission = self.reddit.submission(url=url)
        submission.comments.replace_more(limit=None)
        self.count = self.get_replies_count(submission.comments, 0)
        for comment in submission.comments:
            self.add_to_tree(comment)

    def get_replies_count(self, comments, count):
        for comment in comments:
            count += 1
            reps = comment.replies
            if reps:
                count = self.get_replies_count(reps, count)
        return count

    def add_to_tree(self, comment):
        # Adds 'comment' to Tree
        try:
            self.tree.insert('', 'end', id=self.id, values=[comment.body])
            if comment.replies:
                self.get_subs(comment, self.id)
            self.id += 1
        except:             # Smileys are a struggle...
            pass

    def get_subs(self, comment, id):
        # Gets Possible Responses to Comments
        id2 = 0
        for reply in comment.replies:
            did = str(id)+str('.')+str(id2)
            try:
                self.tree.insert(id, 'end', id=did, values=[reply.body])
                if reply.replies:
                    self.get_subs(reply, did)
            except:
                pass
            id2 += 1

    def clear_tree(self):
        # Clears Tree
        self.tree.delete(*self.tree.get_children())



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
