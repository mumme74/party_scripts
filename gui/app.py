import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from namecard_page import NameCardPage
from project_page import ProjectPage
from placement_page import PlacementPage
from template_page import TemplatePage
from menu import main_menu
from wrap_obj_to_vars import wrap_instance

class GuiApp(tk.Tk):
    def __init__(self, project, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self._project = project
        self.prj_wrapped = wrap_instance(project)
        self.geometry('1024x600')
        self.pages = (ProjectPage, NameCardPage, 
                      PlacementPage, TemplatePage)
        
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.menu = main_menu(self)

        style = ttk.Style(self)
        if style.theme_use() == "aqua":
            # can't set background color on aqua
            style.theme_use('clam')

        self.tab_ctrl = ttk.Notebook(self)
        self.tab_ctrl.pack(expand=True, fill='both')
        
        for i, frm in enumerate(self.pages):
            tab = ttk.Frame(self.tab_ctrl)
            self.tab_ctrl.add(tab, text=frm.name)

            frame = frm(parent=tab, controller=self)
            frame.grid(row=0,column=0, sticky='nsew')
        
        self.tab_ctrl.select(0)
        sett = self.prj_wrapped['settings']
        sett['project_name'] \
            .trace_add('write', lambda *a: self.redraw())
        sett['date'] \
            .trace_add('write', lambda *a: self.redraw())
        self.redraw()

    def redraw(self):
        sett = self.prj_wrapped['settings']
        name = sett['project_name'].get()
        date = sett['date'].get()
        self.title(f'Bordsplacering: {name} {date}')

if __name__ == "__main__":
    app = GuiApp()
    app.mainloop()