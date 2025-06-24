import tkinter as tk
from tkinter import ttk 
from menu import PageHeader

class PlacementPage(ttk.Frame):
    name = "Placerings vy"
    def __init__(self, master, controller):
        ttk.Frame.__init__(self, master)
        self.controller = controller

        PageHeader(self, controller)
