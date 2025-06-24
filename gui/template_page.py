from tkinter import ttk 

class TemplatePage(ttk.Frame):
    name = "Mall vy"
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        lbl = ttk.Label(self, text=self.name, font=controller.title_font)
        lbl.pack(side='top',fill='x', pady=10)
