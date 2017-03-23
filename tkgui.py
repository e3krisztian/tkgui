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
        # XXX: copy-paste Dialog here?
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


class Blueprint:
    """
        A human centric grid layout definition
    """

    def __init__(self, layout_text):
        self.lines = layout_text.rstrip().splitlines()
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


g = Blueprint(
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
assert not g.is_cell(0, 2)  # empty
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

# this defines an invalid tk grid: the cells of x and y overlap
g = Blueprint(
    '''\
    a | b | c
    x     | .
    . |   y .
        z
    ''')

assert g.get_rowspan(0, 0) == 1  # c
assert g.get_rowspan(2, 0) == 2  # c
assert g.get_rowspan(0, 1) == 2  # x


class Attributes:
    '''
        Convenience: name -> value map.

        (object by itself does not work - can not set new attribute)
    '''
    pass


class View:
    def __init__(self, root):
        self.root = root
        self.widgets = Attributes()
        self.variables = Attributes()

    def add_var(self, name, tkvariable):
        setattr(self.variables, name, tkvariable)

    def add_widget(self, name, tkwidget):
        setattr(self.widgets, name, tkwidget)


class ViewBuilder:
    '''
        Base class for constructing and storing widgets

        Construction is done in Blueprint.build()
        During construction widgets are stored as attributes, for accessing/modifying their values
    '''

    DEFVAR_PREFIX = 'variable_'
    MAKE_WIDGET_PREFIX = 'widget_'
    MAKE_SUBFRAME_PREFIX = 'frame_'
    BLUEPRINT_PREFIX = 'blueprint_'
    CONFIG_PREFIX = 'widgetconfig_'
    LABEL_PREFIX = '\''

    def define_variables(self, name, view):
        '''
            Create variable[s] for name [optional]
        '''
        def noop(name, view):
            pass
        define_variables = getattr(self, self.DEFVAR_PREFIX + name, noop)
        define_variables(name, view)

    def make_widget(self, parent, name_or_label, view):
        '''
            Construct a widget by name
        '''
        if name_or_label.startswith(self.LABEL_PREFIX):
            return self.make_label(parent, name_or_label, view)

        construct = getattr(self, self.MAKE_WIDGET_PREFIX + name_or_label, None)
        if construct is None:
            # subframe?
            construct = getattr(self, self.MAKE_SUBFRAME_PREFIX + name_or_label, None)
        if construct is None:
            # subframe via blueprint?
            blueprint = getattr(self, self.BLUEPRINT_PREFIX + name_or_label, None)
            if blueprint:
                if not isinstance(blueprint, Blueprint):
                    blueprint = Blueprint(blueprint)
                def construct(parent, name, view):
                    return self.add_subframe(parent, name, view, blueprint)
        if construct is None:
            # fallback: label
            return self.make_label(parent, name_or_label, view)

        widget = construct(parent, name_or_label, view)
        # NOTE: labels are not stored (they are generally not valid Python identifiers)
        view.add_widget(name_or_label, widget)
        return widget

    def make_label(self, parent, text, view):
        if text.startswith(self.LABEL_PREFIX):
            text = text[len(self.LABEL_PREFIX):]
        return Label(parent, text=text)

    def configure_widget(self, widget, widget_name):
        '''
            Configure padding and stickyness of the widget
        '''
        configure = getattr(self, self.CONFIG_PREFIX + widget_name, None)
        grid_conf = dict(sticky=tk.NSEW)
        if configure is not None:
            grid_conf.update(configure(widget, widget_name))
        widget.grid(**grid_conf)

    def build(self, root, blueprint):
        '''
            Construct widgets and assemble/configure them according to the blueprint
        '''
        view = View(root)
        self.add_widgets(root, view, blueprint)
        self.configure(root, blueprint)
        return view

    def add_widgets(self, parent, view, blueprint):
        for row in range(blueprint.nrows):
            for col in range(blueprint.ncols):
                if blueprint.is_cell(col, row):
                    name = blueprint.get_text(col, row)
                    self.define_variables(name, view)
                    w = self.make_widget(parent, name, view)
                    w.grid(column=col, row=row, columnspan=blueprint.get_colspan(col, row), rowspan=blueprint.get_rowspan(col, row))
                    self.configure_widget(w, name)

    def configure(self, root, blueprint):
        for row in range(blueprint.nrows):
            root.rowconfigure(row, weight=1)
        for col in range(blueprint.ncols):
            root.columnconfigure(col, weight=1)

    def add_subframe(self, parent, name, view, blueprint):
        '''
            Build a sub-frame in view with an independent layout
        '''

        frame = ttk.Frame(view.root)
        view.add_widget(name, frame)
        self.add_widgets(frame, view, blueprint)
        self.configure(frame, blueprint)
        return frame
