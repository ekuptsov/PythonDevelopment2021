import tkinter as tk
from tkinter import messagebox
import re


class Application(tk.Frame):

    GEOM_RE = re.compile(
        r"(?P<row>\d+)"
        r"(?:\.(?P<rowweight>\d+))?"
        r"(?P<height>\+\d+)?"
        ":"
        r"(?P<column>\d+)"
        r"(?:\.(?P<colweight>\d+))?"
        r"(?P<width>\+\d+)?"
        r"(?:/(?P<gravity>[NSWE]{1,4}))?"
    )

    def __init__(self, master=None, title=None):
        super().__init__(master)
        if master:
            self.master = master
        self.master.title(title)
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        self.grid(sticky='NSWE')
        self.createWidgets()

    def createWidgets(self):
        pass

    def apply_geometry(self, row, column, rowweight=1, height=0,
                       colweight=1, width=0, gravity='NSWE'):
        row = int(row)
        column = int(column)
        rowweight = int(rowweight)
        height = int(height)
        colweight = int(colweight)
        width = int(width)
        self.grid(row=row, rowspan=height+1)
        self.master.rowconfigure(row, weight=rowweight)
        self.grid(column=column, columnspan=width+1)
        self.master.columnconfigure(column, weight=colweight)
        self.grid(sticky=gravity)

    def smart_builder(self, tkClass, geometry, **options):
        # check that tkClass belong tk
        class AppTkClass(tkClass, Application):
            pass

        widget = AppTkClass(self, **options)

        match = re.fullmatch(self.GEOM_RE, geometry)
        if match:
            specified = \
                {k: v for k, v in match.groupdict().items() if v is not None}
            widget.apply_geometry(**specified)
        return widget

    def __getattr__(self, name):
        def create_and_set_obj(*args, **kwargs):
            setattr(self, name, self.smart_builder(*args, **kwargs))
        return create_and_set_obj


class App(Application):

    def createWidgets(self):
        self.msg = "Congratulations!\nYou've found a sercet level!"
        self.F1(tk.LabelFrame, "1:0", text="Frame 1")
        self.F1.B1(tk.Button, "0:0/NW", text="1")
        self.F1.B2(tk.Button, "0:1/NE", text="2")
        self.F1.B3(tk.Button, "1:0+1/SEW", text="3")
        self.F2(tk.LabelFrame, "1:1", text="Frame 2")
        self.F2.B1(tk.Button, "0:0/N", text="4")
        self.F2.B2(tk.Button, "0+1:1/SEN", text="5")
        self.F2.B3(tk.Button, "1:0/S", text="6")
        self.Q(tk.Button, "2.0:1.2/SE", text="Quit", command=self.quit)
        self.F1.B3.bind(
            '<Any-Key>',
            lambda event: messagebox.showinfo(self.msg.split()[0], self.msg)
        )


if __name__ == '__main__':
    app = App(title="Sample application")
    app.mainloop()
