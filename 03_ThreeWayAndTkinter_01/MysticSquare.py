import tkinter as tk
from tkinter import messagebox
import random
import itertools
from functools import partial
import math


class MysticSquare(tk.Frame):

    def __init__(self, master=None, *, rows=None, cols=None):
        super().__init__(master)
        if master:
            self.master = master
        self.rows = rows
        self.cols = cols
        self.createFrame()

    def new(self):
        self.shuffle()

    def shuffle(self):
        self.order = \
            list(itertools.product(range(self.rows), range(self.cols)))
        random.shuffle(self.order)

        # set up only len(frame) buttons
        for button, (row, col) in zip(self.frame, self.order):
            button.grid(row=row, column=col, sticky='nswe')

    def player_win(self):
        win_order = itertools.product(range(self.rows), range(self.cols))
        # compare positions only for len(frame) buttons
        decision = all(
            curr == win
            for _, curr, win
            in zip(range(len(self.frame)), self.order, win_order)
        )
        return decision

    def in_bounds(self, i, j):
        return 0 <= i < self.rows and 0 <= j < self.cols

    def move(self, bt_number):
        idx = bt_number - 1
        button = self.frame[idx]
        info = button.grid_info()
        # print(info)
        i, j = info['row'], info['column']
        neighs = ((i-1, j), (i+1, j), (i, j-1), (i, j+1))
        any_empty = [
            (si, sj)
            for si, sj in neighs
            if self.in_bounds(si, sj) and
               not self.grid_slaves(row=si, column=sj)
        ]
        if any_empty:
            si, sj = any_empty.pop()
            button.grid(row=si, column=sj, sticky='nswe')
            self.order[idx] = (si, sj)
            if self.player_win():
                messagebox.showinfo(title='Win', message='Congratulations!')
                self.shuffle()

    def createFrame(self):
        for i in range(self.rows):
            self.rowconfigure(i, weight=1, minsize=80)
        for j in range(self.cols):
            self.columnconfigure(j, weight=1, minsize=80)

        self.frame = []
        for i in range(1, self.rows*self.cols):
            bt = tk.Button(self, text=str(i),
                           command=partial(self.move, i),
                           highlightcolor='white')
            self.frame.append(bt)
        self.shuffle()


class Panel(tk.Frame):

    def __init__(self, master=None, *, rows=None, cols=None):
        super().__init__(master)
        if master:
            self.master = master
        self.rows = rows
        self.cols = cols
        self.createButtons()

    def createButtons(self):
        for i in range(self.cols):
            self.columnconfigure(i, weight=1)
        self.new_bt = tk.Button(self, text='New')
        self.quit_bt = tk.Button(self, text='Quit', command=self.quit)

        half = self.cols / 2
        self.new_bt.grid(row=0, column=0, columnspan=math.ceil(half))
        self.quit_bt.grid(row=0, column=math.floor(half),
                          columnspan=math.ceil(half))


class MysticSquareApp(tk.Frame):

    def __init__(self, master=None, *, rows=4, cols=4):
        super().__init__(master)
        if master:
            self.master = master
        self.master.title('Mystic Square')
        self.grid(sticky='nswe')
        self.rows = rows
        self.cols = cols
        self.createUI()

    def createUI(self):
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)

        self.control_panel = Panel(self, rows=self.rows, cols=self.cols)
        self.control_panel.pack(side=tk.TOP, fill=tk.X)

        self.game = MysticSquare(self, rows=self.rows, cols=self.cols)
        self.game.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
        self.control_panel.new_bt.config(command=self.game.new)


if __name__ == '__main__':
    app = MysticSquareApp(rows=2, cols=2)
    app.mainloop()
