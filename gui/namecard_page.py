import tkinter as tk
from tkinter import font
from tkinter import ttk
from tkinter import colorchooser
from tkinter import filedialog
from PIL import ImageTk
from pathlib import Path
from menu import PageHeader
from src.namecard import load_template, \
                         create_img

class FakeDept:
    name = 'Avd. för tester'

class FakePerson:
    date = '2025-06-16 17:30',
    fname = 'Test'
    lname = 'Testsson'
    email = 'test@fake.com'
    dept = FakeDept()
    def table_id(self):
        return 'Bord 10'


class NameCardPage(ttk.Frame):
    name = "Namnbricke vy"
    def __init__(self, master, controller):
        ttk.Frame.__init__(self, master)
        self.controller = controller
        prj = self.controller.prj_wrapped
        self.settings = sett = prj['settings']
        self.rowconfigure(1, weight=0)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        self.page_hdr = PageHeader(self, controller)

        sel_pane = NameCardProperties(self, controller, width=300)
        sel_pane.columnconfigure(0, weight=1)
        sel_pane.rowconfigure(0, weight=1)
        sel_pane.grid(row=1, column=0, padx=3, sticky='wnes')

        edit_pane = EditNameCard(self, controller)
        edit_pane.columnconfigure(0, weight=1)
        edit_pane.rowconfigure(0, weight=0)
        edit_pane.grid(row=1, column=1, padx=3, sticky='nw')

class NameCardProperties(ttk.LabelFrame):
    def __init__(self, master, controller, **kwargs):
        ttk.LabelFrame.__init__(
            self, master, text='Egenskaper', **kwargs)
        self.controller = controller

        props = PropertyWidget(self, controller)
        props.grid(row=0, column=0, sticky='wnes')

        vscroll = ttk.Scrollbar(self, orient='vertical', command=props.yview)
        props.configure(yscrollcommand=vscroll.set)
        vscroll.grid(row=0, column=1, sticky='nes')

        ttk.Button(self, text='Spara som ny mall',
            command=self.save_as_new_template
        ).grid(row=2, column=0, columnspan=2, sticky='e')
        
    def save_as_new_template(self):
        template_path = Path(__file__).parent.parent / 'templates'
        path = filedialog.asksaveasfilename(
            title='Spara som',initialdir=template_path,
            filetypes=(('Template filer', '*.json'),))
        if path:
            self.controller.project.settings['namecard'] \
                .save_as_new_template(path)

class EditNameCard(ttk.LabelFrame):
    def __init__(self, master, controller, **kwargs):
        ttk.LabelFrame.__init__(
            self, master, text='Förhandgransning', **kwargs)
        self.controller = controller
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.card = controller.prj_wrapped['settings']['namecard']
        self.trace_vars(self.card)
        
        self.canvas = tk.Canvas(
            self, width=600, height=400, 
            background='gray', border=0, 
            borderwidth=0, highlightthickness=0)
        self.canvas.grid(row=1, column=1, sticky='nw')
        ttk.Label(self).grid(row=1, padx=5, pady=5, column=0)

        self.indata_changed()

    def indata_changed(self, *args):
        img, new_size, out_dir, card = load_template(
            self.controller.project)
        img_card = create_img(img, card, new_size, FakePerson())

        imgtk = ImageTk.PhotoImage(img_card)
        self.canvas.delete('all')
        self.canvas.create_image(0,0, image=imgtk, anchor=tk.NW)

    def trace_vars(self, obj):
        def cb(*args):
            self.after(1, self.indata_changed)
            
        if isinstance(obj, dict):
            for k,v in obj.items():
                if not isinstance(v, tk.Variable):
                    self.trace_vars(v)
                else:
                    v.trace_add('write', cb)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                if not isinstance(v, tk.Variable):
                    self.trace_vars(v)
                else:
                    v.trace_add('write', cb)


class PropertyWidget(ttk.Treeview):
    def __init__(self, master, controller, **kwargs):
        cols=('Egenskap', 'värde')
        ttk.Treeview.__init__(self, master, columns=cols, **kwargs)
        
        self.controller = controller
        self.namecard = controller.project.settings['namecard']
        namecard_wrapped = controller.prj_wrapped['settings']['namecard']

        for c in cols:
            self.heading(c, text=c)
        self.column(cols[0], width=100, minwidth=0, stretch=False)
        self.column(cols[1], width=180, minwidth=0, stretch=False)
        self.column('#0', width=20, minwidth=0, stretch=False)

        self.recreate()

        self.bind('<Double-1>', self.dbl_clicked)
        controller.bind('<<Reload>>', self.recreate)

    def variable_for(self, iid):
        key = self.item(iid).get('values')[0].strip()
        master_iid = self.parent(iid)
        card = self.controller.prj_wrapped['settings']['namecard']
        if master_iid:
            master = self.item(master_iid).get('values')[0]
            return key, card[master][key]
        else:
            return key, card[key]

    def dbl_clicked(self, event):
        iid = self.identify_row(event.y)
        col = self.identify_column(event.x)
        if not iid or not col or col == '#0':
            return
        
        vlus = self.item(iid)
        values = vlus.get('values')
        if len(values) < 2:
            return # not a value item, it's a root for subitems
        
        bbox = self.bbox(iid, '#2')
        key, variable = self.variable_for(iid)

        match values[0].strip():
            case 'pos':
                PosEdit(self, variable, iid, bbox)
            case 'color':
                ColorEdit(self, variable, iid, bbox)
            case 'align':
                vlus = ('absolute', 'center')
                ComboBoxEdit(
                    self, variable, iid, bbox, values=vlus)
            case 'font':
                FontSelector(self, variable, iid, bbox)
            case _ :
                if key == 'template_json':
                    pth = PathEdit(self, variable, iid, bbox, 
                                   None, (('Template files', '*.json'),))
                    if pth.ok:
                        print('reload namecard')
                elif key == 'template_png':
                    p = self.controller.project.settings['namecard'].template_json
                    PathEdit(self, variable, iid, bbox, 
                             Path(p).parent, (('PNG file', '*.png'),))
                elif isinstance(variable.get(), bool):
                    vlus=('True', 'False')
                    ComboBoxEdit(self, variable, iid, bbox, 
                                 values=vlus, 
                                 convert=lambda v: True if v == 'True' else False)
                elif isinstance(variable.get(), int):
                    IntEdit(self, variable, iid, bbox)
                else:
                    StringEdit(self, variable, iid, bbox)

    def recreate(self):
        self.delete(*self.get_children())

        for k,v in self.namecard.__dict__.items():
            if hasattr(v, '__dict__'):
                root = self.insert('','end',values=(k))
                for k1,v1 in v.__dict__.items():
                    if isinstance(v1, (list, tuple)):
                        v1 = ", ".join(str(i) for i in v1)
                        v1 = f'({v1})'
                    self.insert(root,'end',values=(f'  {k1}',v1))
            else:
                self.insert('','end',k, values=(k,v))

class IntEdit(ttk.Spinbox):
    def __init__(self, master, variable, iid, bbox):
        var = tk.IntVar(value=variable.get())
        ttk.Spinbox.__init__(
            self, master, textvariable=var,
            from_=-100000, to=100000)

        self.variable = variable
        self.iid = iid
        self.bbox = bbox
        self._var = var

        self.place(x=bbox[0],y=bbox[1],
                   w=bbox[2], h=bbox[3])
        self.bind('<Return>', self.set_value)
        self.bind('<FocusOut>', self.on_focus_out)

        self.focus()

    def on_focus_out(self, event):
        self.destroy()

    def set_value(self, event):
        self.variable.set(self._var.get())
        vlus = self.master.item(self.iid).get('values')
        vlus[1] = self._var.get()
        self.master.item(self.iid, values=vlus)
        self.destroy()

class StringEdit(ttk.Entry):
    def __init__(self, master, variable, iid, bbox):
        var = tk.StringVar(value=variable.get())

        ttk.Entry.__init__(
            self, master, textvariable=var, width=bbox[2])
        self.iid = iid
        self.variable = variable
        self.bbox = bbox
        self._var = var
        self.place(x=bbox[0],y=bbox[1],
                   w=bbox[2], h=bbox[3])
        self.bind('<Return>', self.set_value)
        self.bind('<FocusOut>', self.on_focus_out)

        self.focus()

    def on_focus_out(self, event):
        self.destroy()

    def set_value(self, event):
        self.variable.set(self._var.get())
        vlus = self.master.item(self.iid).get('values')
        vlus[1] = self._var.get()
        self.master.item(self.iid, values=vlus)
        self.destroy()

class PosEdit(ttk.Frame):
    def __init__(self, master, variable, iid, bbox):
        ttk.Frame.__init__(
            self, master, width=bbox[2],height=bbox[3]*2)
        self.variable = variable
        self.iid = iid
        self.bbox = bbox

        self._var = tk.StringVar(
            value=f'({variable[0].get()}, {variable[1].get()})')
        self.x_var = tk.StringVar(value=variable[0].get())
        self.y_var = tk.StringVar(value=variable[1].get())
        self.x_var.trace_add('write', self._changed)
        self.y_var.trace_add('write', self._changed)

        self.place(x=bbox[0], y=bbox[1])
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
        self.x_spin.bind('<Return>', self.set_value)
        self.x_spin.bind('<FocusOut>', self.on_focus_out)

        # Y coordinate
        ttk.Label(self, text='y:').grid(
            row=1, column=2, sticky='wn')
        self.y_spin = ttk.Spinbox(
            self, width=4, to=2000, textvariable=self.y_var)
        self.y_spin.grid(row=1, column=3, sticky='wn')
        self.y_spin.bind('<Return>', self.set_value)
        self.y_spin.bind('<FocusOut>', self.on_focus_out)

        self.x_spin.focus()

    def set_value(self, event):
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

    def on_focus_out(self, event):
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

class ComboBoxEdit(ttk.Combobox):
    def __init__(self, master, variable, iid, bbox, **kwargs):
        var = tk.StringVar(value=variable.get())
        self.convert = kwargs.pop('convert', lambda v: v)

        ttk.Combobox.__init__(
            self, master, width=bbox[2], 
            textvariable=var, **kwargs)

        self.variable = variable
        self.iid = iid
        self.bbox = bbox
        self._var = var

        self.place(x=bbox[0],y=bbox[1],
                   w=bbox[2], h=bbox[3])
        
        self.bind('<Return>', self.set_value)
        self.bind('<FocusOut>', self.on_focus_out)

    def on_focus_out(self, event):
        self.destroy()

    def set_value(self, event):
        vlu = self.convert(self._var.get())
        self.variable.set(vlu)
        vlus = self.master.item(self.iid).get('values')
        vlus[1] = self._var.get()
        self.master.item(self.iid, values=vlus)
        self.destroy()

class FontSelector(ttk.Frame):
    def __init__(self, master, variable, iid, bbox):
        ttk.Frame.__init__(
            self, master, width=bbox[2],height=bbox[3]*2)
        
        self._var = tk.StringVar(value=variable.get())
        self._var.trace_add('write', self.changed_vlu)
        self.variable = variable
        self.iid = iid

        self.place(x=bbox[0], y=bbox[1])

        # show the font in the Entry box
        self.families = font.families()
        self.edit = ttk.Entry(self, textvariable=self._var)
        self.edit.grid(row=0, column=0, sticky='wne')
        self.edit.bind('<FocusOut>', self.on_focus_out)
        self.edit.bind('<Return>', self.set_value)

        self.combobox = ttk.Combobox(
            self, textvariable=self._var, values=self.families)
        self.combobox.grid(row=1, column=0, sticky='wnes')
        self.combobox.bind('<FocusOut>', self.on_focus_out)
        self.combobox.bind('<Return>', self.set_value)
        self.combobox.focus()

        self.changed_vlu() # update with current font

    def changed_vlu(self, *args):
        cur_font = self._var.get()
        if cur_font in self.families:
            self.edit.configure(font=font.Font(family=cur_font))
        else:
            self.edit.configure(font=font.Font())
        self.edit.update()

    def on_focus_out(self, event):
        foc = self.focus_get()
        if foc != self.edit and foc != self.combobox:
            self.destroy()

    def set_value(self, event):
        self.variable.set(self._var.get())
        vlus = self.master.item(self.iid).get('values')
        vlus[1] = self._var.get()
        self.master.item(self.iid, values=vlus)
        self.destroy()
