from __future__ import unicode_literals, print_function

import tkgui as gui


class LoginBuilder(gui.ViewBuilder):

    # variables for widgets
    def def_string_var(self, name, view):
        view.add_var(name, gui.tk.StringVar())

    defvar_username = def_string_var
    defvar_password = def_string_var

    # widget constructors
    def make_username(self, name, view):
        view.variables.username.set(name)
        return gui.ttk.Entry(view.root, textvariable=view.variables.username)

    def make_password(self, name, view):
        view.variables.password.set(name)
        return gui.ttk.Entry(view.root, textvariable=view.variables.password, show='*')

    def make_quit(self, name, view):
        return gui.Button(view.root, text='Quit', command=view.root.quit, underline=0)

    # widget configurators for minor changes - padding and stickyness
    def conf_quit(self, widget, name):
        return dict(sticky=gui.tk.E)


blueprint = gui.Blueprint('''\
    Username: | username
    Password: | password
    quit
    ''')

root = gui.tk.Tk()
view = LoginBuilder().build(root, blueprint)
view.root.mainloop()

print('username:', view.variables.username.get())
print('password:', view.variables.password.get())
