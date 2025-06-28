import tkinter as tk
from sys import platform
from tkinter import ttk
from tkinter import font as tkfont
from tkinter import filedialog
from tkinter import messagebox
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from namecard_page import NameCardPage
from project_page import ProjectPage
from placement_page import PlacementPage
from src.exceptions import AppException
from src.project import Project
from menu import main_menu
import wrap_obj_to_vars as wrap
from undo_redo import Undo, UndoDisable, \
                      UndoTransaction

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, project, app):
        FileSystemEventHandler.__init__(self)
        self._project = project
        self._app = app

    def on_modified(self, event):
        file = Path(event.src_path)
        for prop in ('persons', 'departments','tables'):
            path = self._project.settings[prop]['file']
            if file.absolute() == path.absolute():
                self._app.indata_file_changed(prop, path)

class GuiApp(tk.Tk):
    def __init__(self, project, proj_path):
        tk.Tk.__init__(self)
        self.rebuild_ui(project, proj_path)

    def rebuild_ui(self, project, proj_path):
        self.option_add('*tearOff', False)
        self.project = project
        if proj_path:
            try:
                self.project.open_project(proj_path)
            except AppException as e:
                msg = f'{e.__class__.__name__}\n {e}'
                self.after(100, lambda *a:
                    self.show_error(f'Fel vid laddning: {msg}'))
            else:
                unique = set()
                for unk in self.project.persons.unknown_dept():
                    if unk not in unique:
                        def closeure(msg):
                            return lambda *a: self.show_error(msg)
                        self.after(100, closeure(f'Avdelning okänd: {unk}'))
                    unique.add(unk)
                    msg = None # break ref so self.after works
                
        self.prj_wrapped = wrap.wrap_instance(project)
        self.geometry('1024x610')
        self.pages = (ProjectPage, NameCardPage, PlacementPage)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # file change observer
        self._file_observer = Observer()
        self._file_evt = FileChangeHandler(project, self)
        self.trace_indata_files()
        self._file_observer.start()
        self.last_indata_change = None # workaround as events can't pass values
        
        self.setup_events()

        self.header_var = tk.StringVar()
        
        self.title_font = tkfont.Font(
            family='Helvetica', size=18, weight="bold", slant="italic")
        self.menu = main_menu(self)

        style = ttk.Style(self)
        if style.theme_use() == "aqua":
            # can't set background color on aqua
            style.theme_use('clam')

        self.tab_ctrl = ttk.Notebook(self)
        self.tab_ctrl.grid(row=0, column=0, sticky='nsew')
        self.tab_ctrl.rowconfigure(0, weight=1)
        self.tab_ctrl.columnconfigure(0, weight=1)

        # add tabs and pages
        for i, frm in enumerate(self.pages):
            tab = ttk.Frame(self.tab_ctrl)
            self.tab_ctrl.add(tab, text=frm.name, sticky='nsew') 
            
            tab.rowconfigure(0, weight=1)
            tab.columnconfigure(0, weight=1)

            frame = frm(master=tab, controller=self)
            frame.grid(row=0,column=0, ipadx=3, sticky='nsew')
        
        # switch undo when changing pages
        self.tab_ctrl.bind('<<NotebookTabChanged>>', 
            lambda e: Undo.set_current(self.current_page().undo))
        Undo.set_current(self.current_page().undo)
        
        # default to project page
        self.tab_ctrl.select(0)

        sett = self.prj_wrapped['settings']  
        sett['project_name'].trace_add('write', 
            lambda *a: self.title_changed())
        sett['date'].trace_add('write', 
            lambda *a: self.title_changed())
        self.prj_wrapped['_has_changed'] \
            .trace_add('write',
              lambda *a: self.title_changed())
        
        self.title_changed()

    def title_changed(self):
        sett = self.prj_wrapped['settings']
        name = sett['project_name'].get()
        date = sett['date'].get()[:16]
        change = ' [•]' if self.prj_wrapped['_has_changed'].get() else ''
        self.title(f'Bordsplacering: {name} {date} {change}')
        self.header_var.set(f'{name} {date} {change}')

    def setup_events(self):
        ctrl = 'Command' if platform == 'darwin' else 'Control'
        self.bind_all(f'<{ctrl}-z>', lambda a:Undo.ref().undo())
        self.bind_all(f'<{ctrl}-Shift-Z>', lambda a:Undo.ref().redo())
        self.bind_all(f'<{ctrl}-s>', self.save)
        self.bind_all(f'<{ctrl}-Shift-S>', self.save_as)
        self.bind_all(f'<{ctrl}-o>', self.open)
        self.trace_indata_files()

    def current_page(self):
        tab_id = self.tab_ctrl.select()
        tab = self.tab_ctrl.nametowidget(tab_id)
        frm_id = list(tab.children.keys())[0]
        return tab.children[frm_id]

    def show_message(self, text):
        self.current_page().page_hdr \
            .msgs.add_message(text)
        
    def show_error(self, text): 
        self.current_page().page_hdr \
            .msgs.add_error(text)

    def trace_indata_files(self):
        self._file_observer.unschedule_all()

        sett = self.project.settings
        dirs = set() # get unique
        for prop in ('persons', 'departments','tables'):
            dirs.add(str(sett[prop]['file'].parent.absolute()))
 
        for dir in dirs:
            self._file_observer.schedule(
                self._file_evt, dir, recursive=True)

    def indata_file_changed(self, prop, path):
        self.last_indata_change = prop
        self.reload_project(prop)
        self.event_generate(
            '<<IndataReloaded>>', data=prop)

        self.last_indata_change = None

    def _rewrap(self, prop):
        try:
            if not prop:
                wrap.reload_wrapped(self.prj_wrapped, self.project)
            else:
                props = {
                    'persons':     self.project.persons,
                    'departments': self.project.departments,
                    'tables':      self.project.tables
                }
                if not prop in props.keys():
                    return

                wrap.reload_wrapped(self.prj_wrapped[prop], props[prop])
                wrap.reload_item(self.prj_wrapped['settings'], prop,
                                self.project.settings[prop], 
                                self.project.settings, {})
        except AppException as e:
            self.show_error(str(e))
        self.trace_indata_files()

    def rewrap_project(self, prop=None, transaction=False):
        if not transaction:
            with UndoDisable(Undo.ref()):
                self._rewrap(prop)
        else:
            with UndoTransaction(Undo.ref()):
                self._rewrap(prop)


    def reload_project(self, prop=None):
        self.project.reload(prop)
        self.rewrap_project(prop)


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
            with UndoDisable(Undo.ref()):
                self.prj_wrapped['settings'] \
                    ['project_file_path'].set(Path(path))
        self.prj_wrapped['_has_changed'].set(False)

    def save(self, *args):
        path = str(self.project.settings['project_file_path'])
        if not path or path == '.':
            self.save_as(*args)
        else:
            self.project.save_project()
        self.prj_wrapped['_has_changed'].set(False)

    def open(self, *args):
        path = self.project.settings['project_file_path'] 
        path = path if str(path) else Path('')
        path = filedialog.askopenfilename(
            defaultextension='*.json',
            initialdir=path.parent, initialfile=path.name,
            title='Open project')
        if path:
            self.project.open_project(path)
            self.rebuild_ui(self.project, path)

    def new_project(self, *args):
        self.project = Project()
        self.rebuild_ui(self.project, '')
