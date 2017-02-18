from __future__ import unicode_literals, print_function

try:
    try:
        # python3
        # https://docs.python.org/3.6/library/tkinter.html
        import tkinter as tk
        from tkinter import ttk
        from tkinter.simpledialog import Dialog  # it also has a new SimpleDialog
    except ImportError:
        # python2
        import Tkinter as tk
        import ttk
        # http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
        # http://epydoc.sourceforge.net/stdlib/tkSimpleDialog.Dialog-class.html
        from tkSimpleDialog import Dialog

    has_gui = bool(tk and ttk)
    assert has_gui
except ImportError:
    # there is no tkinter, or ttk
    has_gui = False

Frame = ttk.Frame
Label = ttk.Label
Button = ttk.Button

COLSEP = '|'
EMPTY = ''
VERTICAL_CONTINUATION = '.'


class HGrid:
    """
        Human grid layout definition
    """

    def __init__(self, text):
        self.lines = text.rstrip().splitlines()
        self.nrows = len(self.lines)
        self.cell_columns = self._calculate_cell_columns()
        self.ncols = len(self.cell_columns)

    def _calculate_cell_columns(self):
        positions = {0}
        for line in self.lines:
            match_position = -1
            search = True
            while search:
                match_position = line.find(COLSEP, match_position + 1)
                has_match = match_position != -1
                if has_match:
                    positions.add(match_position + 1)
                search = has_match
        return sorted(positions)

    def _is_left_closed_cell(self, col, row):
        """
            Is col at the left side of a cell?
        """
        line = self.lines[row]
        colsep = self.cell_columns[col]
        return col == 0 or line[colsep - 1:colsep] == COLSEP

    def is_cell(self, col, row):
        """
            Is it the top-left corner of a cell?
        """
        return self._is_left_closed_cell(col, row) and self.get_text(col, row) not in [EMPTY, VERTICAL_CONTINUATION]

    def get_text(self, col, row):
        line = self.lines[row]
        colpos = self.cell_columns[col]
        text, _, _ = line[colpos:].partition(COLSEP)
        return text.strip()

    def get_colspan(self, col, row):
        line = self.lines[row]
        colpos = self.cell_columns[col]
        spanend = line.find(COLSEP, colpos)
        if spanend < 0:
            spanend = len(line)
        for i, pos in enumerate(self.cell_columns):
            if pos > spanend:
                return i - col
        return self.ncols - col

    def _is_vertical_continuation(self, col, row):
        return self._is_left_closed_cell(col, row) and self.get_text(col, row) == VERTICAL_CONTINUATION

    def get_rowspan(self, col, row):
        def span_from(row):
            if row == self.nrows:
                return 0
            if self._is_vertical_continuation(col, row):
                return 1 + span_from(row + 1)
            return 0
        return 1 + span_from(row + 1)


g = HGrid(
    '''\
    a | b | c
    x     | .
      |   y
         z
    ''')

assert g.is_cell(0, 0)  # a
assert g.is_cell(1, 0)  # b
assert g.is_cell(0, 1)  # x
assert not g.is_cell(1, 1)  # continuation - horizontal
assert not g.is_cell(2, 1)  # continuation - vertical
assert not g.is_cell(0, 2)  #  empty
assert g.is_cell(1, 2)  # y
assert g.is_cell(0, 3)  # z
try:
    g.is_cell(0, 4)
    assert False, 'IndexError expected'
except IndexError:
    pass

assert g.get_text(1, 0) == 'b'
assert g.get_text(0, 1) == 'x'
assert g.get_text(0, 3) == 'z'

assert g.get_colspan(0, 0) == 1
assert g.get_colspan(2, 0) == 1
assert g.get_colspan(1, 2) == 2  # y
assert g.get_colspan(0, 3) == 2  # z

assert g.get_rowspan(0, 0) == 1  # a
assert g.get_rowspan(0, 1) == 1  # x
assert g.get_rowspan(1, 0) == 1  # b
assert g.get_rowspan(2, 0) == 2  # c

# this is an invalid tk grid: the cells of x and y overlap
g = HGrid(
    '''\
    a | b | c
    x     | .
    . |   y .
        z
    ''')

assert g.get_rowspan(0, 0) == 1  # c
assert g.get_rowspan(2, 0) == 2  # c
assert g.get_rowspan(0, 1) == 2  # x

g = HGrid(
    '''\
    alpha |          b | c
    x long text        | .
          |   y          widget
          z
    ''')

from random import randint
def randbyte():
    return randint(60, 240)
    return randint(0, 255)

def color(col, row):
    r, g, b = randbyte(), randbyte(), randbyte()
    return '#%02x%02x%02x' % (r, g, b)

root = tk.Tk()
# using Frame as root fails to expand its content if window is resized
# root = Frame(height=1000, width=800)
# root.grid(sticky=tk.NSEW)

# overlapping grids do not work:
# tk.Button(root, bg=color(0,0), text='1g.get_text(col, row)', anchor='s').grid(column=0, row=0, columnspan=2, rowspan=2, sticky='NWES')
# tk.Button(root, bg=color(1,1), text='2g.get_text(col, row)', anchor='s').grid(column=1, row=1, columnspan=2, rowspan=2, sticky='NWES')
# root.mainloop()

print(Dialog)
grid = None
for row in range(g.nrows):
    for col in range(g.ncols):
        if g.is_cell(col, row):
            # Label(root, background=color(col, row), text=g.get_text(col, row)).grid(column=col, row=row, columnspan=g.get_colspan(col, row), rowspan=g.get_rowspan(col, row), sticky='NWES')
            w = tk.Button(root, bg=color(col, row), text=g.get_text(col, row), anchor='se')
            w.grid(column=col, row=row, columnspan=g.get_colspan(col, row), rowspan=g.get_rowspan(col, row), sticky='NWES')
            # w.rowconfigure(row, weight=1)
            # w.columnconfigure(col, weight=1)
            grid = w
            print(col, row)
            for f in (g.get_text, g.get_colspan, g.get_rowspan):
                print(f.__name__, f(col, row))

for row in range(g.nrows):
    root.rowconfigure(row, weight=row, minsize=100)
    # grid.rowconfigure(row, weight=1)
for col in range(g.ncols):
    root.columnconfigure(col, weight=col, minsize=200)
    # grid.columnconfigure(col, weight=1)
root.mainloop()
