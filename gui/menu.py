
import tkinter as tk 
from tkinter import ttk

class PageHeader(ttk.Frame):
    def __init__(self, page, controller, **kwargs):
        ttk.Frame.__init__(self, page, **kwargs)
        self.controller = controller
        #self.rowconfigure(2, weight=1)
        self.grid(row=0, column=0, columnspan=2, sticky='wne')

        # undo redo buttons
        u_btn = ttk.Button(self, text='<', width=1,
            command=lambda *a:controller.event_generate('<<undo>>'))
        u_btn.grid(row=0, column=0, pady=5, padx=2, sticky='wn')
        
        r_btn = ttk.Button(self, text='>', width=1,
            command=lambda *a: controller.event_generate('<<redo>>'))
        r_btn.grid(row=0, column=1, pady=5, padx=2, sticky='wn')
        
         # page header
        lbl = ttk.Label(self, textvariable=controller.header_var, 
                        font=controller.title_font)
        lbl.grid(row=0, column=2, pady=10, padx=3, sticky='wne')

def main_menu(window, undo):
    # Creating Menubar
    menubar = tk.Menu(window)
    # Adding File Menu and commands
    file = tk.Menu(menubar, tearoff = 0)
    menubar.add_cascade(label ='File', menu = file)
    file.add_command(label ='New File', command = None)
    file.add_command(label ='Open...', command = None)
    file.add_command(label ='Save', command = None)
    file.add_separator()
    file.add_command(label ='Exit', command = window.destroy)

    # Adding Edit Menu and commands
    edit = tk.Menu(menubar, tearoff = 0)
    menubar.add_cascade(label ='Edit', menu = edit)
    edit.add_command(label='Undo', command=lambda *a: undo.undo())
    edit.add_command(label='Redo', command=lambda *a: undo.redo())
    edit.add_separator()
    edit.add_command(label ='Cut', command = None)
    edit.add_command(label ='Copy', command = None)
    edit.add_command(label ='Paste', command = None)
    edit.add_command(label ='Select All', command = None)
    edit.add_separator()
    edit.add_command(label ='Find...', command = None)
    edit.add_command(label ='Find again', command = None)

    # Adding Help Menu
    help_ = tk.Menu(menubar, tearoff = 0)
    menubar.add_cascade(label ='Help', menu = help_)
    help_.add_command(label ='Tk Help', command = None)
    help_.add_command(label ='Demo', command = None)
    help_.add_separator()
    help_.add_command(label ='About Tk', command = None)

    window.config(menu = menubar)