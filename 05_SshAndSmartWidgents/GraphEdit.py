''' Draft of Editor's frames interaction

----- Canvas -> Text interaction -----
activation -> action -> logging
(1) after activation choose action (move/create-resize)
(2) action interract with figure pull:
      -- move: take exisited figure and update its coords
      -- c-r : add new figure in pull
How present figure pull?
own pull and every time redraw on tk.Text or
redraw in-place (inside _move and _resize events with tk.Text.search)

----- Text -> Canvas interaction -----
text <<Modified>> event
finding difference:
(1) "new" string is wrong -> tag it in red
w/  figure pull: figures -- fig_pull;
                 text    -- self.text.get('all')
w/o figure pull: figures -- descriptions(canvas.find_all))
                 text    -- self.text.get('all')
"new": figures _subset_of_ text
(2) string is edited ->
if wrong: tag in red and remove figure
    else: find id and changes and apply .itemconfigure()
"edited": removed := figures - text
          added   := text - figures

This implementation works without own figure_pull.
Instead it calls tk.Text.search and tk.Canvas.find_all
to manage figures
'''

import tkinter as tk
from functools import partial
from typing import List
import random
import re

class Editor(tk.Frame):

    figure_description = '{type} {coords!s:^25} {width} {outline} {fill}\n'
    available_colors = ("white black red green"
                        " blue cyan yellow magenta"
                       ).split()

    DESCR_RE = re.compile(
        r"(?P<type>oval)"
        r" +"
        r"(?P<coords>\[\d+, \d+, \d+, \d+\])"
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
        self.createCanvas()
        self.createText()

    def _draw(self, type: str, coords: List[str],
              width: str, outline: str, fill: str):
        # print(type, coords, width, outline, fill)
        x0, y0, x1, y1 = eval(coords)
        # print(x0, y0, x1, y1)
        self.canvas.create_oval(
            x0, y0, x1, y1, fill=fill, width=width, outline=outline)

    def _mark(self, line):
        pass

    def _modified(self, event):
        # print('mody')
        text = set(self.text.get('1.0', tk.END).strip().split('\n'))
        figure_descriptions = set(
            self._description(Id)[:-1]  # '\n' awkward :(
            for Id in
            self.canvas.find_all()
        )
        if figure_descriptions < text:
            # add new lines
            new = next(iter(text - figure_descriptions))
            m = re.fullmatch(self.DESCR_RE, new)
            if m:
                # print('newfig')
                self._draw(**m.groupdict())
            else:
                # print('mark in red')
                self._mark(new)
        elif figure_descriptions - text:
            # edit existed lines
            # print('edit')
            removed = figure_descriptions - text
            added = text - figure_descriptions
            # print(f'removed={removed}')
            # print(f'added={added}')
            m = re.fullmatch(self.DESCR_RE, removed.pop())
            if m:
                x0, y0, x1, y1 = eval(m.group('coords'))
                w = float(m.group('width')) / 2
                Ids = self.canvas.find_enclosed(x0-w, y0-w, x1+w, y1+w)
                Id = next(iter(Ids), None)
                self.canvas.delete(Id)
            m = re.fullmatch(self.DESCR_RE, added.pop())
            if m:
                self._draw(**m.groupdict())
        self.text.edit_modified(0)

    def _user_edit(self, event):
        self.text.edit_modified(0)
        self.text.bind('<<Modified>>', self._modified)

    def createText(self):
        self.text = tk.Text(self, height=20, width=50, font=('Helvetica', '14'))
        self.text.grid(row=0, column=0)
        self.figures_set = set()
        self.text.bind('<Button-1>', self._user_edit)

    def _description(self, Id, options=None):
        config = self.canvas.itemconfigure(Id)
        figure = dict(
            type=self.canvas.type(Id),
            coords=list(map(int, self.canvas.coords(Id))),
            width=float(config['width'][-1]),
            outline=config['outline'][-1],
            fill=config['fill'][-1],
        )
        if options:
            figure.update(options)
        return self.figure_description.format(**figure)

    def _replace_text(self, Id, old_coords):
        old_descr = self._description(Id, {'coords': old_coords})
        new_descr = self._description(Id)
        i = self.text.search(old_descr, index='1.0')
        self.text.delete(i, i+' lineend')
        self.text.insert(i, new_descr.strip('\n'))  # '\n' awkward :(

    def _move(self, event, Id, mouse_figure):
        mx, my = mouse_figure
        # x0, y0, *_ = self.canvas.coords(Id)
        coords = list(map(int, self.canvas.coords(Id)))
        x0, y0, x1, y1 = coords
        xAmount = event.x - (x0 + mx)
        yAmount = event.y - (y0 + my)
        self.canvas.move(Id, xAmount, yAmount)
        new_coords = x0+xAmount, y0+yAmount, x1+xAmount, y1+yAmount
        # print(coords)
        self._replace_text(Id, old_coords=coords)

    def _resize(self, event, Id, pivot):
        p0, p1 = pivot
        coords = list(map(int, self.canvas.coords(Id)))
        x0, y0, x1, y1 = coords
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
        self._replace_text(Id, old_coords=coords)
        # self.canvas.coords(Id)
        # self.canvas.coords(Id, x0, y0, event.x - x0, event.y - y0)

    # def _totext(self, event, Id, prev_coords=None):
    #     config = self.canvas.itemconfigure(Id)
    #     coords = list(map(int, self.canvas.coords(Id)))
    #     figure = dict(
    #         type=self.canvas.type(Id),
    #         coords=coords,
    #         width=config['width'][-1],
    #         outline=config['outline'][-1],
    #         fill=config['fill'][-1],
    #     )
    #     if prev_coords:
    #         prevfigure = figure.copy()
    #         prevfigure['coords'] = prev_coords
    #         prev_descr = self.figure_description.format(**prevfigure).strip()
    #         txt = [line for line in self.text.get('1.0', tk.END).split('\n')
    #                if line != '']
    #         # print(txt)
    #         # print(prev_descr)
    #         # i = txt.index(prev_descr)
    #         # self.text.delete(f'{i+1}.0', f'{i+1}.end')
    #         txt.remove(prev_descr)
    #         self.text.delete('1.0', tk.END)
    #         concat = '\n'.join(txt)+'\n' if txt else ''
    #         # print('add', '\n'.join(txt))
    #         self.text.insert(tk.END, concat)
    #         self.figures_set.discard(prev_descr)
    #         # print(self.figures_set)
    #     descr = self.figure_description.format(**figure).strip()
    #     self.figures_set.add(descr)
    #     self.text.insert(tk.END, descr+'\n')


    def _activation(self, event):
        self.text.edit_modified(1) # lock text self-updating
        x0, y0 = float(event.x), float(event.y)
        overlap = self.canvas.find_overlapping(x0, y0, x0, y0)
        Id = next(reversed(overlap), None)  # a little hack
        if not Id:
            # create new figure
            fill = random.choice(self.available_colors)
            outline = random.choice(self.available_colors)
            width = random.randint(1, 5)
            Id = self.canvas.create_oval(
                x0, y0, x0+1, y0+1, fill=fill, width=width, outline=outline)
            self.text.insert(tk.END, self._description(Id))
            action = partial(self._resize, Id=Id, pivot=(x0, y0))
            # logging = partial(self._totext, Id=Id)
        else:
            # move existing figure
            xx0, yy0, xx1, yy1 = list(map(int, self.canvas.coords(Id)))
            # mouse coords relative to the left corner of the figure
            # mouse_figure is constant during the motion
            mx, my = x0 - xx0, y0 - yy0
            action = partial(self._move, Id=Id, mouse_figure=(mx, my))
            # logging = partial(self._totext, Id=Id, prev_coords=[xx0, yy0, xx1, yy1])
        self.canvas.bind('<B1-Motion>', action)
        # self.canvas.bind('<ButtonRelease-1>', logging)


    def createCanvas(self):
        self.canvas = tk.Canvas(self, height=400, width=400)
        self.canvas.grid(row=0, column=1)
        self.canvas.bind('<Button-1>', self._activation)


if __name__ == '__main__':
    editor = Editor(title='Graph Edit')
    editor.mainloop()