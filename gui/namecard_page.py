import os, json
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk
from pathlib import Path
from menu import PageHeader
from undo_redo import Undo, \
                      UndoDisable, \
                      UndoSnapshot, \
                      UndoTransaction
from src.project import NameCard
from src.namecard import load_template, \
                         create_img
from common_widgets import IntEdit, \
                           StringEdit, \
                           PosEdit, \
                           ColorEdit, \
                           PathEdit, \
                           ComboBoxEdit, \
                           FontSelector, \
                           DialogBase

template_dir = Path(__file__).parent.parent / 'templates'

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

        self.sel_pane = NameCardProperties(self, controller, width=300)
        self.sel_pane.columnconfigure(0, weight=1)
        self.sel_pane.rowconfigure(0, weight=1)
        self.sel_pane.grid(row=1, column=0, padx=3, sticky='wnes')

        self.view_pane = PreviewNameCard(self, controller)
        self.view_pane.columnconfigure(0, weight=1)
        self.view_pane.rowconfigure(0, weight=0)
        self.view_pane.grid(row=1, column=1, padx=3, sticky='nw')

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

        # buttons at bottom
        btn_frm = ttk.Frame(self)
        btn_frm.grid(row=2, column=0, columnspan=2, sticky='wne')
        btn_frm.columnconfigure(0, weight=1)

        ttk.Button(btn_frm, text='Andra mallar',
            command=self.select_template
        ).grid(row=2, column=0, sticky='w')

        ttk.Button(btn_frm, text='Spara som ny mall',
            command=self.save_as_new_template
        ).grid(row=2, column=1, sticky='e')
        
    def save_as_new_template(self):
        template_path = Path(__file__).parent.parent / 'templates'
        path = filedialog.asksaveasfilename(
            title='Spara som',initialdir=template_path,
            filetypes=(('Template filer', '*.json'),))
        if path:
            self.controller.project.settings['namecard'] \
                .save_as_new_template(path)
            
    def change_card_template(self, namecard):
        banned = ('greet',)
        def card(obj, src):
            if isinstance(obj, (list, tuple)):
                obj = {i:v for i,v in enumerate(obj)}
            for k,v in obj.items():
                ks = str(k)
                if hasattr(src, '__dict__') and obj[k] is not None:
                    card(obj, src.__dict__)
                elif isinstance(obj[k], (dict,list,tuple)):
                    card(obj[k], src[k])
                elif not ks.startswith('_') and not ks in banned:
                    obj[k].set(src[k])

        obj = self.controller.prj_wrapped['settings']['namecard']
        card(obj, namecard)


    def select_template(self, *Äevent):
        dlg = SelectTemplateDlg(self, self.controller)
        if dlg.selected:
            self.master.view_pane.set_disable(True)
            with UndoTransaction(Undo.ref()):
                self.change_card_template(dlg.selected)
            self.after(200, lambda *a:
                self.master.view_pane.set_disable(False) or \
                self.master.view_pane.indata_changed(True) or \
                self.master.sel_pane.props.recreate()
            )
            

            
    def undo_events(self, event):
        with UndoDisable(self.master.undo):
            self.props.recreate()

class PreviewNameCard(ttk.LabelFrame):
    def __init__(self, master, controller, **kwargs):
        ttk.LabelFrame.__init__(
            self, master, text='Förhandgransning', **kwargs)
        self.controller = controller
        self.columnconfigure(0, weight=1)
        self._disable = False

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
        if self._disable: 
            return
        
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

    def set_disable(self, dis):
        self._disable = dis


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

class SelectTemplateDlg(DialogBase):
    def __init__(self, master, controller, **args):
        args['width'] = 300
        args['height'] = 500
        DialogBase.__init__(
            self, master, controller, **args)
        
        self.selected = None

         # header
        ttk.Label(
            self, text='Välj mall!',
            font=controller.title_font
        ).grid(row=0, column=0, columnspan=3,
            sticky='nwe', pady=5, padx=5)
        
        # show available templates
        self.tbl = ttk.Treeview(self)
        self.tbl.grid(row=1, column=0, sticky='nws')
        # scroll from template table
        vscroll = ttk.Scrollbar(
            self, orient='vertical', command=self.tbl.yview)
        self.tbl.configure(yscrollcommand=vscroll.set)
        vscroll.grid(row=1, column=1, sticky='nes')

        # show preview of selected
        self.canvas = tk.Canvas(
            self, width=300, height=200,
            #background='gray', border=0,
            #borderwidth=0, highlightbackground=0
            )
        self.canvas.grid(row=1, column=2, sticky='nw')

        self.after(100, lambda *a: self.reload())

        # cancel and OK btns
        ttk.Button(
            self, text='Avbryt', command=self.reject
        ).grid(row=2, column=0, sticky='w', padx=5, pady=5)

        self.ok = ttk.Button(
            self, text='OK', command=self.accept)
        self.ok.grid(row=2, column=2, sticky='e', padx=5, pady=5)

        self.load_templates()
        self.build_tbl()

        self.tbl.bind('<<TreeviewSelect>>', self.reload)

        self.make_modal() # must be last in func


    def current(self):
        "Return currently selected"
        sel = self.tbl.focus()
        if not sel: 
            return None

        for i,(path,obj) in enumerate(self.templates.items()):
            if i == self.tbl.index(sel):
                card = {
                    'greet': obj['name'],
                    'template': template_dir / path,
                    'card': obj
                }
                return NameCard(card)

    def make_img(self, template, image_size):
        img, new_size, out_dir, card = load_template(
            self.controller.project, template, image_size)
        img_card = create_img(img, card, image_size, FakePerson())

        return ImageTk.PhotoImage(img_card)

    def reload(self, *args):
        template = self.current()
        if not template: return
        sz = (int(self.canvas['width']), 
              int(self.canvas['height']))
        imgtk = self.make_img(template, sz)
        self.canvas.delete('all')
        self.canvas.create_image(
            0,0, image=imgtk, anchor=tk.NW)     
 
    def load_templates(self):
        tmplts = []
        for _, _, files in os.walk(template_dir):
            tmplts += [Path(f) for f in files if f.endswith('.json')]
        
        self.templates = {}
        for file in tmplts:
            try:
                with open(template_dir / file) as fp:
                    self.templates[f'{file}'] = json.load(fp)
                    self.templates[f'{file}']['template_json'] = str(file)
            except (IOError, json.JSONDecodeError):
                pass

    def build_tbl(self):
        tbl = self.tbl
        cols = ('Namn','Grundbild')
        
        self.tbl.configure(columns=cols)
        for c in cols:
            self.tbl.heading(c, text=c)

        self.tbl.column('#0', width=0, minwidth=0, stretch=False)
        self.tbl.column(cols[0], width=150, minwidth=0, stretch=False)
        self.tbl.column(cols[1], width=150, minwidth=0, stretch=False)

        for f,t in self.templates.items():
            vlus = (t['name'], t['template_png'])
            tbl.insert('','end', values=vlus)

    def accept(self, *event):
        self.selected = self.current()
        self.destroy()