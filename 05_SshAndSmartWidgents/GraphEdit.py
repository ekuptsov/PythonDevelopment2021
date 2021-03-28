import tkinter as tk
from functools import partial
import random
import re

class Editor(tk.Frame):

    figure_decription = '{type} {coords!s:^30} {width} {outline} {fill}\n'
    available_colors = ("white black red green"
                        " blue cyan yellow magenta"
                       ).split()

    DESCR_RE = re.compile(
        r"(?P<type>oval)"
        r" +"
        r"(?P<coords>\[\d+\.\d+, \d+\.\d+, \d+\.\d+, \d+\.\d+\])"
        r" +"
        r"(?P<width>\d+\.\d+) "
        rf"(?P<outline>{'|'.join(available_colors)}) "
        rf"(?P<fill>{'|'.join(available_colors)})"
    )

    def __init__(self, master=None, title=None):
        super().__init__(master)
        if master:
            self.master = master
        self.master.title(title)
        self.grid(sticky='nswe')
        self.createGraph()
        self.createText()

    def _draw(self, type, coords, width, outline, fill):
        # print(type, coords, width, outline, fill)
        x0, y0, x1, y1 = eval(coords)
        # print(x0, y0, x1, y1)
        self.canvas.create_oval(
            x0, y0, x1, y1, fill=fill, width=width, outline=outline)

    def _modified(self, event):
        widget_text = self.text.get('1.0', tk.END).split('\n')

        red = []
        green = []
        figures_set = set()
        # print(self.figures_set)
        for i, line in enumerate(widget_text, 1):
            if not line:
                continue
            m = re.fullmatch(self.DESCR_RE, line)
            # m = re.findall(self.DESCR_RE, line)
            # print(m)
            if m:
                # figure = {k: eval(val) for k, val in m.groupdict().items()}
                descr = self.figure_decription.format(**m.groupdict()).strip()
                # print(descr)
                if descr not in self.figures_set:
                    print('draw')
                    self._draw(**m.groupdict())
                    # print('draw ', descr)
                figures_set.add(descr)
            else:
                red.append(i)

        for fig in (self.figures_set - figures_set):
            # print('del ', fig)
            # print(self.figures_set)
            # print(figures_set)
            # # m = re.findall(self.DESCR_RE, fig)
            # # print('del', m)
            m = re.fullmatch(self.DESCR_RE, fig)
            # print('del', m)
            if m:
                x0, y0, x1, y1 = eval(m.group('coords'))
                # print(x0, y0, x1, y1)
                Ids = self.canvas.find_enclosed(x0-1, y0-1, x1+1, y1+1)
                # print(Ids)
                for Id in Ids:
                    self.canvas.delete(Id)
        self.figures_set = figures_set
        # print(self.figures_set)
        self.text.edit_modified(0)

    def createText(self):
        self.text = tk.Text(self, height=20, width=50, font=('Helvetica', '14'))
        self.text.grid(row=0, column=0)
        self.text.edit_modified(0)
        self.figures_set = set()
        self.text.bind('<<Modified>>', self._modified)


    def _move(self, event, Id, mouse_figure):
        mx, my = mouse_figure
        x0, y0, *_ = self.canvas.coords(Id)
        xAmount = event.x - (x0 + mx)
        yAmount = event.y - (y0 + my)
        self.canvas.move(Id, xAmount, yAmount)

    def _resize(self, event, Id, pivot):
        p0, p1 = pivot
        x0, y0, x1, y1 = self.canvas.coords(Id)
        # identify part of plane (SE, NE, NW, SW)
        if pivot == (x0, y1):
            y0, y1 = y1, y0
        elif pivot == (x1, y0):
            x0, x1 = x1, x0
        elif pivot == (x1, y1):
            y0, y1 = y1, y0
            x0, x1 = x1, x0

        scalex = (event.x - x0) / (x1 - x0)
        scaley = (event.y - y0) / (y1 - y0)
        if scalex == 0: scalex = 1
        if scaley == 0: scaley = 1
        self.canvas.scale(Id, p0, p1, scalex, scaley)
        # self.canvas.coords(Id)
        # self.canvas.coords(Id, x0, y0, event.x - x0, event.y - y0)

    def _totext(self, event, Id, prev_coords=None):
        config = self.canvas.itemconfigure(Id)
        figure = dict(
            type=self.canvas.type(Id),
            coords=self.canvas.coords(Id),
            width=config['width'][-1],
            outline=config['outline'][-1],
            fill=config['fill'][-1],
        )
        if prev_coords:
            prevfigure = figure.copy()
            prevfigure['coords'] = prev_coords
            prev_descr = self.figure_decription.format(**prevfigure).strip()
            txt = [line for line in self.text.get('1.0', tk.END).split('\n')
                   if line != '']
            # print(txt)
            # print(prev_descr)
            # i = txt.index(prev_descr)
            # self.text.delete(f'{i+1}.0', f'{i+1}.end')
            txt.remove(prev_descr)
            self.text.delete('1.0', tk.END)
            concat = '\n'.join(txt)+'\n' if txt else ''
            # print('add', '\n'.join(txt))
            self.text.insert(tk.END, concat)
            self.figures_set.discard(prev_descr)
            # print(self.figures_set)
        descr = self.figure_decription.format(**figure).strip()
        self.figures_set.add(descr)
        self.text.insert(tk.END, descr+'\n')


    def _activation(self, event):
        x0, y0 = float(event.x), float(event.y)
        overlap = self.canvas.find_overlapping(x0, y0, x0, y0)
        Id = next(reversed(overlap), None)  # a little hack
        if not Id:
            # create new figure
            color = random.choice(self.available_colors)
            outline = random.choice(self.available_colors)
            width = random.randint(1, 5)
            Id = self.canvas.create_oval(
                x0, y0, x0+1, y0+1, fill=color, width=width, outline=outline)
            # figure.update(self.canvas.itemconfigure(Id))
            # self.text.edit_modified(0)
            action = partial(self._resize, Id=Id, pivot=(x0, y0))
            logging = partial(self._totext, Id=Id)
        else:
            # move existing figure
            xx0, yy0, xx1, yy1 = self.canvas.coords(Id)
            # mouse coords relative to the left corner of the figure
            # mouse_figure is constant during the motion
            mx, my = x0 - xx0, y0 - yy0
            action = partial(self._move, Id=Id, mouse_figure=(mx, my))
            logging = partial(self._totext, Id=Id, prev_coords=[xx0, yy0, xx1, yy1])

        self.canvas.bind('<B1-Motion>', action)
        self.canvas.bind('<ButtonRelease>', logging)

    def createGraph(self):
        self.canvas = tk.Canvas(self, height=400, width=400)
        self.canvas.grid(row=0, column=1)
        self.canvas.bind('<Button>', self._activation)
        # helv36 = tkFont.Font(family='Helvetica',
        # size=36, weight='bold')


if __name__ == '__main__':
    editor = Editor(title='Graph Edit')
    editor.mainloop()