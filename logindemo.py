from __future__ import unicode_literals, print_function

import tkgui as gui


class LoginWidgets(gui.Widgets):

    # widget constructors
    def make_username(self, parent, name):
        self.var_username = v = gui.tk.StringVar()
        v.set(name)
        return gui.ttk.Entry(parent, textvariable=v)

    def make_password(self, parent, name):
        self.var_password = v = gui.tk.StringVar()
        v.set(name)
        return gui.ttk.Entry(parent, textvariable=v, show='*')

    def make_quit(self, parent, name):
        return gui.Button(parent, text='Quit', command=parent.quit, underline=0)

    # widget configurators for minor changes - padding and stickyness
    def conf_quit(self, widget, name):
        return dict(sticky=gui.tk.E)


blueprint = gui.Blueprint('''\
    Username: | username
    Password: | password
    quit
    ''')

root = gui.tk.Tk()
widgets = LoginWidgets()
widgets.build(root, blueprint)
root.mainloop()

print('username', widgets.var_username.get())
print('password', widgets.var_password.get())
