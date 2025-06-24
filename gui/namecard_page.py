import tkinter as tk
from tkinter import ttk 

class NameCardPage(ttk.Frame):
    name = "Namnbricke vy"
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        lbl = ttk.Label(self, text=self.name, font=controller.title_font)
        lbl.pack(side='top',fill='x', pady=10)
