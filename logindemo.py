from __future__ import unicode_literals, print_function

import tkgui as gui


class LoginBuilder(gui.ViewBuilder):

    # variables for widgets
    def def_string_variable(self, name, view):
        view.add_var(name, gui.tk.StringVar())

    variable_username = def_string_variable
    variable_password = def_string_variable

    # widget constructors
    def widget_username(self, parent, name, view):
        view.variables.username.set(name)
        return gui.ttk.Entry(parent, textvariable=view.variables.username)

    def widget_password(self, parent, name, view):
        view.variables.password.set(name)
        return gui.ttk.Entry(parent, textvariable=view.variables.password, show='*')

    def widget_quit(self, parent, name, view):
        return gui.Button(parent, text='Quit', command=view.root.quit, underline=0)

    # widget configurators for minor changes - padding and stickyness
    def widgetconfig_quit(self, widget, name):
        # return dict()
        return dict(sticky=gui.tk.W)

    def widgetconfig_login(self, widget, name):
        widget.config(borderwidth=1, relief=gui.tk.RIDGE)
        return dict()

    blueprint_login = '''\
        Username: | username
        Password: | password
        '''

    blueprint_exit = '''\
        Exit: | quit
        '''

app_blueprint = gui.Blueprint('''\
    Login/exit demo | login | exit
    ''')

root = gui.tk.Tk()
view = LoginBuilder().build(root, app_blueprint)
view.root.mainloop()

print('username:', view.variables.username.get())
print('password:', view.variables.password.get())
