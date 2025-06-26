import tkinter as tk
from tkinter import ttk
from menu import PageHeader

class TemplatePage(ttk.Frame):
    name = "Mall vy"
    def __init__(self, master, controller):
        ttk.Frame.__init__(self, master)
        self.controller = controller
        
        self.page_hdr = PageHeader(self, controller)
