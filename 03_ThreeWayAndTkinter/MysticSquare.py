import tkinter as tk
import random
import itertools

ROWS = 4
COLUMNS = 4


class MysticSquare(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.grid(sticky=tk.N+tk.E+tk.W+tk.S)
        self.createWidgets()

    def shuffle(self):
        cols, rows = self.grid_size()
        sticky = tk.N+tk.E+tk.W+tk.S
        indexies = list(itertools.product(range(1, rows), range(cols)))
        random.shuffle(indexies)

        for button, (row, column) in zip(self.table, indexies):
            button.grid(row=row, column=column, sticky=sticky)

    def createWidgets(self):
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)

        self.new_bt = tk.Button(self, text='New', command=self.shuffle)
        self.quit_bt = tk.Button(self, text='Quit', command=self.quit)
        self.new_bt.grid(row=0, column=0, columnspan=COLUMNS // 2)
        self.quit_bt.grid(row=0, column=COLUMNS // 2, columnspan=COLUMNS // 2)

        for i in range(1, ROWS+1):
            self.rowconfigure(i, weight=1, minsize=80)

        for j in range(COLUMNS):
            self.columnconfigure(j, weight=1, minsize=80)

        self.table = [
            tk.Button(self, text=f'{i}')
            for i in range(1, ROWS*COLUMNS)
        ]
        self.shuffle()


def main():
    app = MysticSquare()
    app.master.title('Mystic Square')
    app.mainloop()


if __name__ == '__main__':
    main()
