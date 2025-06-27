import tkinter as tk
from tkinter import ttk
from menu import PageHeader
from undo_redo import Undo

class TemplatePage(ttk.Frame):
    name = "Mall vy"
    def __init__(self, master, controller):
        ttk.Frame.__init__(self, master)
        self.controller = controller
        
        self.page_hdr = PageHeader(self, controller)
        self.undo = Undo(self, controller.prj_wrapped)
