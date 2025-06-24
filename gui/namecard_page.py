import tkinter as tk
from tkinter import ttk 
from menu import PageHeader

class NameCardPage(ttk.Frame):
    name = "Namnbricke vy"
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller

        PageHeader(self, controller)
