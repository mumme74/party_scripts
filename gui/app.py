import tkinter as tk
from sys import platform
from tkinter import ttk
from tkinter import font as tkfont
from namecard_page import NameCardPage
from project_page import ProjectPage
from placement_page import PlacementPage
from template_page import TemplatePage
from menu import main_menu
from wrap_obj_to_vars import wrap_instance
from undo_redo import Undo

class GuiApp(tk.Tk):
    def __init__(self, project, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.option_add('*tearOff', False)
        self.project = project
        self.prj_wrapped = wrap_instance(project)
        self.undo = Undo(self.prj_wrapped)
        self.geometry('1024x600')
        self.pages = (ProjectPage, NameCardPage, 
                      PlacementPage, TemplatePage)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
        self.setup_events()

        self.header_var = tk.StringVar()
        
        self.title_font = tkfont.Font(
            family='Helvetica', size=18, weight="bold", slant="italic")
        self.menu = main_menu(self, self.undo)

        style = ttk.Style(self)
        if style.theme_use() == "aqua":
            # can't set background color on aqua
            style.theme_use('clam')

        self.tab_ctrl = ttk.Notebook(self)
        self.tab_ctrl.pack(expand=True, fill='both')
        
        for i, frm in enumerate(self.pages):
            tab = ttk.Frame(self.tab_ctrl)
            self.tab_ctrl.add(tab, text=frm.name)

            frame = frm(master=tab, controller=self)
            frame.grid(row=0,column=0, ipadx=3, sticky='wnes')
        
        self.tab_ctrl.select(0)

        sett = self.prj_wrapped['settings']  
        sett['project_name'].trace_add('write', 
            lambda *a: self.title_changed())
        sett['date'].trace_add('write', 
            lambda *a: self.title_changed())
        self.title_changed()

    def title_changed(self):
        sett = self.prj_wrapped['settings']
        name = sett['project_name'].get()
        date = sett['date'].get()[:16]
        self.title(f'Bordsplacering: {name} {date}')
        self.header_var.set(f'{name} {date}')

    def setup_events(self):
        self.bind('<<undo>>', lambda a:self.undo.undo())
        self.bind('<<redo>>', lambda a:self.undo.redo())
        ctrl = 'Command' if platform == 'darwin' else 'Control'
        self.bind_all(f'<{ctrl}-z>', lambda a:self.undo.undo())
        self.bind_all(f'<{ctrl}-Shift-Z>', lambda a:self.undo.redo())
