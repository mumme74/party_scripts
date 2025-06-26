import tk
from tkinter import ttk
from tkinter import filedialog
from pathlib import Path

class LookupPath(ttk.Frame):
    def __init__(self, master, variable, type, 
                 settings, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        self.textvariable = variable
        self.settings = settings
        self.type = type

        entry = ttk.Entry(self, textvariable=variable)
        entry.columnconfigure(0, weight=1)
        entry.rowconfigure(0, weight=1)
        entry.grid(row=0, column=0, sticky="we")

        button = ttk.Button(self, text="Sök", width=5,
                            command=lambda *a: self.open())
        button.grid(row=0, column=1, sticky="E")

    def open(self):
        initvlu = Path(self.textvariable.get() or \
                       self.settings['project_file_path'])
        if initvlu.is_file():
            initfile = initvlu.name
            initvlu = initvlu.parent

        match self.type:
            case 'dir':
                vlu = filedialog.askdirectory(
                    initialdir=initvlu)
            case 'file_open':
                vlu = filedialog.askopenfile(
                    initialdir=initvlu, initialfile=initfile)
                if vlu:
                    vlu = vlu.name
            case 'file_save':
                vlu = filedialog.askopenfilename(
                    initialdir=initvlu, initialfile=initfile)
            case _:
                return

        if vlu:
            self.textvariable.set(vlu)
