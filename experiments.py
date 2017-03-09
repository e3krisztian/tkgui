from __future__ import unicode_literals, print_function

import tkgui as gui
from random import randint


g = gui.Blueprint(
    '''\
    alpha |          b | c
    x long text        | .
          |   y          widget
          z
    ''')


def randcolor():
    return randint(60, 240)
    # return randint(0, 255)


def color(col, row):
    r, g, b = randcolor(), randcolor(), randcolor()
    return '#%02x%02x%02x' % (r, g, b)


# gui.tk.NoDefaultRoot()
root = gui.tk.Tk()
root.grid()
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

# root = gui.tk.Frame(root, background=color(0,0))
root = gui.tk.Frame(root)
# root.grid()
root.grid(sticky=gui.tk.NSEW)

# overlapping grids do not work:
# gui.tk.Button(root, bg=color(0,0), text='1g.get_text(col, row)', anchor='s').grid(column=0, row=0, columnspan=2, rowspan=2, sticky='NWES')
# gui.tk.Button(root, bg=color(1,1), text='2g.get_text(col, row)', anchor='s').grid(column=1, row=1, columnspan=2, rowspan=2, sticky='NWES')
# root.mainloop()

for row in range(g.nrows):
    for col in range(g.ncols):
        if g.is_cell(col, row):
            # Label(root, background=color(col, row), text=g.get_text(col, row)).grid(column=col, row=row, columnspan=g.get_colspan(col, row), rowspan=g.get_rowspan(col, row), sticky='NWES')
            w = gui.tk.Button(root, bg=color(col, row), text=g.get_text(col, row), anchor='se')
            w.grid(column=col, row=row, columnspan=g.get_colspan(col, row), rowspan=g.get_rowspan(col, row), sticky=gui.tk.NSEW)
            print(col, row)
            for f in (g.get_text, g.get_colspan, g.get_rowspan):
                print(f.__name__, f(col, row))

for row in range(g.nrows):
    root.rowconfigure(row, weight=row)
    # root.rowconfigure(row, weight=row, minsize=100)
    # root.rowconfigure(row, weight=1)
for col in range(g.ncols):
    root.columnconfigure(col, weight=col)
    # root.columnconfigure(col, weight=col, minsize=200)
    # root.columnconfigure(col, weight=1)
root.mainloop()
