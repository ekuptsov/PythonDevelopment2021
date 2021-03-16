import tkinter as tk
from tkinter import messagebox
import random
import itertools
from functools import partial
from math import ceil

ROWS = 4
COLUMNS = 4


class MysticSquare(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.grid(sticky='nswe')
        self.createWidgets()

    def shuffle(self):
        cols, rows = self.grid_size()
        self.order = list(itertools.product(range(1, rows), range(cols)))
        random.shuffle(self.order)
        del self.order[-1]  # now len(order) == len(table)

        for button, (row, column) in zip(self.table, self.order):
            button.grid(row=row, column=column, sticky='nswe')

    def player_win(self):
        cols, rows = self.grid_size()
        win_order = itertools.product(range(1, rows), range(cols))
        decision = all(curr == win for curr, win in zip(self.order, win_order))
        return decision

    def in_bounds(self, i, j):
        cols, rows = self.grid_size()
        return 1 <= i < rows and 0 <= j < cols

    def move(self, bt_number):
        idx = bt_number - 1
        button = self.table[idx]
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

    def createWidgets(self):
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)

        self.new_bt = tk.Button(self, text='New', command=self.shuffle)
        self.quit_bt = tk.Button(self, text='Quit', command=self.quit)
        self.new_bt.grid(row=0, column=0, columnspan=ceil(COLUMNS/2))
        self.quit_bt.grid(row=0, column=COLUMNS // 2, columnspan=ceil(COLUMNS/2))

        for i in range(1, ROWS+1):
            self.rowconfigure(i, weight=1, minsize=80)

        for j in range(COLUMNS):
            self.columnconfigure(j, weight=1, minsize=80)

        self.table = []
        for i in range(1, ROWS*COLUMNS):
            bt = tk.Button(self, text=str(i),
                           command=partial(self.move, i),
                           highlightcolor='white')
            self.table.append(bt)
        self.shuffle()


def main():
    app = MysticSquare()
    app.master.title('Mystic Square')
    app.mainloop()


if __name__ == '__main__':
    main()
