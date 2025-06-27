import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk
from pathlib import Path
from menu import PageHeader
from undo_redo import Undo, UndoDisable
from src.namecard import load_template, \
                         create_img
from common_widgets import IntEdit, \
                           StringEdit, \
                           PosEdit, \
                           ColorEdit, \
                           PathEdit, \
                           ComboBoxEdit, \
                           FontSelector

class FakeTbl:
    id = 'Bord 10'

class FakeDept:
    name = 'Avd. för tester'

class FakePerson:
    date = '2025-06-16 17:30',
    fname = 'Test'
    lname = 'Testsson'
    email = 'test@fake.com'
    dept = FakeDept()
    def table(self):
        return FakeTbl()


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
        self.undo = Undo(self, controller.prj_wrapped)

        self.page_hdr = PageHeader(self, controller)

        sel_pane = NameCardProperties(self, controller, width=300)
        sel_pane.columnconfigure(0, weight=1)
        sel_pane.rowconfigure(0, weight=1)
        sel_pane.grid(row=1, column=0, padx=3, sticky='wnes')

        edit_pane = PreviewNameCard(self, controller)
        edit_pane.columnconfigure(0, weight=1)
        edit_pane.rowconfigure(0, weight=0)
        edit_pane.grid(row=1, column=1, padx=3, sticky='nw')

class NameCardProperties(ttk.LabelFrame):
    def __init__(self, master, controller, **kwargs):
        ttk.LabelFrame.__init__(
            self, master, text='Egenskaper', **kwargs)
        self.controller = controller

        self.props = PropertyWidget(self, controller)
        self.props.grid(row=0, column=0, sticky='wnes')
        master.bind('<<Undo>>', self.undo_events, add='+')
        master.bind('<<Redo>>', self.undo_events, add='+')

        vscroll = ttk.Scrollbar(self, orient='vertical', 
                command=self.props.yview)
        self.props.configure(yscrollcommand=vscroll.set)
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
            
    def undo_events(self, event):
        with UndoDisable(self.master.undo):
            self.props.recreate()

class PreviewNameCard(ttk.LabelFrame):
    def __init__(self, master, controller, **kwargs):
        ttk.LabelFrame.__init__(
            self, master, text='Förhandgransning', **kwargs)
        self.controller = controller
        self.columnconfigure(0, weight=1)

        self.card = controller.prj_wrapped['settings']['namecard']
        self.trace_vars(self.card)
        
        self.canvas = tk.Canvas(
            self, width=600, height=400, 
            background='gray', border=0, 
            borderwidth=0, highlightthickness=0)
        self.canvas.grid(row=1, column=1, sticky='nw')
        ttk.Label(self).grid(row=1, padx=5, pady=5, column=0)

        self.after(100, lambda *a:
            self.indata_changed())

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
                                 convert_to_str=lambda v: 'True' if v else 'False',
                                 convert_back=lambda v: v == 'True')
                elif isinstance(variable.get(), int):
                    IntEdit(self, variable, iid, bbox)
                else:
                    StringEdit(self, variable, iid, bbox)

    def recreate(self):
        # store folds and scroll
        opened = [self.item(c)['values'][0]
            for i,c in enumerate(self.get_children())
            if self.item(c)['open']
        ]
        scroll = self.yview()
                
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
        
        # restore expanded leaves
        for ch in self.get_children():
            itm = self.item(ch)
            if itm['values'][0] in opened:
                self.item(ch, open=1)
        self.yview(tk.MOVETO, scroll[0])
