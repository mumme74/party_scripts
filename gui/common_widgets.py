import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
from tkinter import colorchooser
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


class EditProperty(ttk.Frame):
    def __init__(self, master, variable, iid, bbox, **kw):
        ttk.Frame.__init__(self, master, **kw)
        self.variable = variable
        if isinstance(variable, tk.Variable):
            self._var = type(variable)(value=variable.get())
        elif isinstance(variable, (list, tuple)):
            self._var = [type(v)(value=v.get()) 
                         for v in variable]
        elif isinstance(variable, dict):
            self._var = {k:type(v)(value=v.get())
                         for k,v in variable}
        self.iid = iid
        self.bbox = bbox

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # default placement, subclass can re-place
        self.place(x=bbox[0],y=bbox[1],
                   w=bbox[2], h=bbox[3])

        self.bind('<Escape>', self.reject)
        self.bind('<FocusOut>', self.accept)
        self.bind('<Return>', self.accept)

    def reject(self, *event):
        self.destroy()

    def accept(self, *event):
        pass # subclass must implement

class IntEdit(EditProperty):
    def __init__(self, master, variable, iid, bbox):
        EditProperty.__init__(
            self, master, variable, iid, bbox)
        
        self.spin = ttk.Spinbox(
            self, textvariable=self._var,
            from_=-100000, to=100000)
        self.spin.grid(sticky='we')
        self.spin.bind('<Return>', self.accept)

        self.spin.focus()

    def accept(self, event):
        self.variable.set(self._var.get())
        vlus = self.master.item(self.iid).get('values')
        vlus[1] = self._var.get()
        self.master.item(self.iid, values=vlus)
        self.destroy()

class StringEdit(EditProperty):
    def __init__(self, master, variable, iid, bbox):
        EditProperty.__init__(
            self, master, variable, iid, bbox)

        self.entry = ttk.Entry(
            self, textvariable=self._var)
        self.entry.grid(sticky='we')
        self.entry.bind('<Return>', self.accept)

        self.entry.focus()

    def accept(self, event):
        self.variable.set(self._var.get())
        vlus = self.master.item(self.iid).get('values')
        vlus[1] = self._var.get()
        self.master.item(self.iid, values=vlus)
        self.destroy()

class PosEdit(EditProperty):
    def __init__(self, master, variable, iid, bbox):
        EditProperty.__init__(
            self, master, variable, iid, bbox,
            width=bbox[2], height=bbox[3]*2+10)

        self._var = tk.StringVar(
            value=f'({variable[0].get()}, {variable[1].get()})')
        self.x_var = tk.StringVar(value=variable[0].get())
        self.y_var = tk.StringVar(value=variable[1].get())
        self.x_var.trace_add('write', self._changed)
        self.y_var.trace_add('write', self._changed)

        self.place(x=bbox[0], y=bbox[1], height=self['height'])
        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, weight=1)

        self.edit = ttk.Entry(self, textvariable=self._var)
        self.edit.state(['disabled'])
        self.edit.grid(row=0, column=0, 
                  columnspan=4, sticky='wne')

        # X coordinate
        ttk.Label(self, text='x:').grid(
            row=1, column=0, padx=3, sticky='wn')
        self.x_spin = ttk.Spinbox(
            self, width=4, to=2000, textvariable=self.x_var)
        self.x_spin.grid(row=1, column=1, sticky='wn')
        self.x_spin.bind('<Return>', self.accept)

        # Y coordinate
        ttk.Label(self, text='y:').grid(
            row=1, column=2, sticky='wn')
        self.y_spin = ttk.Spinbox(
            self, width=4, to=2000, textvariable=self.y_var)
        self.y_spin.grid(row=1, column=3, sticky='wn')
        self.y_spin.bind('<Return>', self.accept)

        self.x_spin.focus()

    def accept(self, event):
        x = int(self.x_var.get())
        y = int(self.y_var.get())
        x1 = self.variable[0].get()
        y1 = self.variable[1].get()
        if x != x1:
            self.variable[0].set(x)
        if y != y1:
            self.variable[1].set(y)
        
        vlus = self.master.item(self.iid).get('values')
        vlus[1] = f'({x}, {y})'
        self.master.item(self.iid, values=vlus)

        self.destroy()

    def reject(self, event):
        foc = self.focus_get()
        if foc != self.x_spin and foc != self.y_spin:
            self.destroy()

    def _changed(self, *args):
        v = f'({self.x_var.get()}, {self.y_var.get()})'
        self._var.set(v)

class ColorEdit:
    def __init__(self, master, variable, iid, bbox):
        color = colorchooser.askcolor(
            title='Välj färg', color=variable.get(), 
            master=master)
        if color and color[1]:
            variable.set(color[1])
            vlus = master.item(iid).get('values')
            vlus[1] = color[1]
            master.item(iid, values=vlus)

class PathEdit:
    def __init__(self, master, variable, iid, bbox, indir, filetypes):
        in_dir = indir.absolute() if indir else \
            (Path(__file__).parent.parent / 'templates').absolute()
        file = Path(variable.get()).name

        vlu = filedialog.askopenfilename(
                initialdir=in_dir, initialfile=file,
                filetypes=filetypes)
        if vlu:
            new_dir = Path(vlu).absolute().parent
            if indir:
                if in_dir != new_dir:
                    master.controller.show_error(
                        f'Filen måste finnas i mappen: {indir}')
                    return
                vlu = Path(vlu).name
            
            variable.set(vlu) 
            vlus = master.item(iid).get('values')
            vlus[1] = vlu
            master.item(iid, values=vlus)

class ComboBoxEdit(EditProperty):
    def __init__(self, master, variable, iid, bbox, **kw):
        self.convert_to_str = kw.pop('convert_to_str', lambda v: v)
        self.convert_back = kw.pop('convert_back', lambda v: v)
        width = kw.pop('width', bbox[2])
        vlus = kw.pop('values', [])

        EditProperty.__init__(
            self, master, variable, 
            iid, bbox, width=width, **kw)
        
        self._var = tk.StringVar(
            value=self.convert_to_str(self._var.get()))
        
        self.combo = ttk.Combobox(
            self, textvariable=self._var,
            values=vlus, **kw)
        self.combo.grid(sticky='we')
        self.combo.bind('<Return>', self.accept)

        self.combo.focus()

    def accept(self, event):
        vlu = self.convert_back(self._var.get())
        self.variable.set(vlu)
        vlus = self.master.item(self.iid).get('values')
        vlus[1] = self._var.get()
        self.master.item(self.iid, values=vlus)
        self.destroy()

class FontSelector(EditProperty):
    def __init__(self, master, variable, iid, bbox):
        EditProperty.__init__(
            self, master, variable, iid, bbox,
            width=bbox[2],height=bbox[3]*2)

        self._var.trace_add('write', self.changed_vlu)

        self.place(x=bbox[0], y=bbox[1],
                   h=self['height'])

        # show the font in the Entry box
        self.families = font.families()
        self.edit = ttk.Entry(self, textvariable=self._var)
        self.edit.grid(row=0, column=0, sticky='wne')
        self.edit.bind('<Return>', self.accept)
        self.edit.bind('<Escape>', self.reject)

        self.combobox = ttk.Combobox(
            self, textvariable=self._var, values=self.families)
        self.combobox.grid(row=1, column=0, sticky='wnes')
        self.combobox.focus()
        self.combobox.bind('<Return>', self.accept)
        self.combobox.bind('<Return>', self.reject)

        self.changed_vlu() # update with current font

    def changed_vlu(self, *args):
        cur_font = self._var.get()
        if cur_font in self.families:
            self.edit.configure(font=font.Font(family=cur_font))
        else:
            self.edit.configure(font=font.Font())
        self.edit.update()

    def reject(self, event):
        foc = self.focus_get()
        if foc != self.edit and foc != self.combobox:
            self.destroy()

    def accept(self, event):
        self.variable.set(self._var.get())
        vlus = self.master.item(self.iid).get('values')
        vlus[1] = self._var.get()
        self.master.item(self.iid, values=vlus)
        self.destroy()
