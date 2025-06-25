import tkinter as tk
from sys import platform
from tkinter import ttk
from tkinter import font as tkfont
from tkinter import filedialog
from pathlib import Path
from namecard_page import NameCardPage
from project_page import ProjectPage
from placement_page import PlacementPage
from template_page import TemplatePage
from menu import main_menu
import wrap_obj_to_vars as wrap
from undo_redo import Undo

class GuiApp(tk.Tk):
    def __init__(self, project, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.option_add('*tearOff', False)
        self.project = project
        self.prj_wrapped = wrap.wrap_instance(project)
        self.undo = Undo(self.prj_wrapped)
        self.geometry('1024x610')
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
        self.tab_ctrl.grid(row=0, column=0, sticky='nsew')
        self.tab_ctrl.rowconfigure(0, weight=1)
        self.tab_ctrl.columnconfigure(0, weight=1)

        
        for i, frm in enumerate(self.pages):
            tab = ttk.Frame(self.tab_ctrl)
            self.tab_ctrl.add(tab, text=frm.name, sticky='nsew') 
            
            tab.rowconfigure(0, weight=1)
            tab.columnconfigure(0, weight=1)

            frame = frm(master=tab, controller=self)
            frame.grid(row=0,column=0, ipadx=3, sticky='nsew')
        
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
        self.bind_all(f'<{ctrl}-s>', self.save)
        self.bind_all(f'<{ctrl}-Shift-S>', self.save_as)
        self.bind_all(f'<{ctrl}-o>', self.open)

    def reload(self, table=None):
        self.project.reload(table)
        self.undo.set_disabled(True)
        if not table:
            wrap.reload_wrapped(self.prj_wrapped, self.project)
        else:
            props = {
                'persons':self.project.persons,
                'departments':self.project.departments,
                'tables': self.project.tables
            }
            if not table in props.keys():
                return

            wrap.reload_wrapped(self.prj_wrapped[table], props[table])
            wrap.reload_item(self.prj_wrapped['settings'], table,
                             self.project.settings[table], {})
        
        self.undo.set_disabled(False)

    def save_as(self, *args):
        path = self.project.settings['project_file_path']
        path = filedialog.asksaveasfilename(
            defaultextension='*.json',
            filetypes=(('Projectfile','*.json'),),
            title='Spara project som',
            initialfile=path.name,
            initialdir=str(path.parent))
        if path:
            self.project.save_project_as(path)
            self.prj_wrapped['settings'] \
                ['project_file_path'].set(Path(path))

    def save(self, *args):
        path = str(self.project.settings['project_file_path'])
        if not path or path == '.':
            self.save_as(*args)
        else:
            self.project.save_project()

    def open(self, *args):
        path = self.project.settings['project_file_path'] 
        path = path if str(path) else Path('')
        path = filedialog.askopenfilename(
            defaultextension='*.json',
            initialdir=path.parent, initialfile=path.name,
            title='Open project')
        if path:
            self.project.open_project(path)
            wrap.reload_wrapped(self.prj_wrapped, self.project)
            self.event_generate('<<Reloaded>>')

