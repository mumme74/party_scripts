import re
import webbrowser
import tkinter as tk
from tkinter import ttk 
from tkinter import messagebox
from pathlib import Path
from menu import PageHeader
from undo_redo import Undo
from common_widgets import LookupPath
from src.namecard import create_name_cards
from src.namecards_docx import create_namecard_docx
from src.tables_docx import create_table_report
from src.special_foods import create_special_foods_report
from src.exceptions import AppException

class PlacementPage(ttk.Frame):
    name = "Placerings vy"
    def __init__(self, master, controller):
        ttk.Frame.__init__(self, master)
        self.controller = controller
        prj = controller.project

        self.page_hdr = PageHeader(self, controller)
        self.undo = Undo(self, controller.prj_wrapped)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        # keep track of how many people to place
        to_place = prj.persons.num_to_place()
        self.num_to_place = tk.IntVar(value=to_place)

        SettingsPane(self, controller
        ).grid(row=1, column=0, sticky='nw', padx=5, pady=5)

        TableViewPane(self, controller
        ).grid(row=1, column=1, sticky='nsew', padx=5, pady=5)

        controller.bind('<<IndataReloaded>>', self.on_indata_reloaded)

    def on_indata_reloaded(self, event):
        err_msg = 'Indata har ändrats, placeringar är ogilltiga'

        if self.controller.last_indata_change == 'persons':
            persons = self.controller.project.persons

            num = persons.num_to_place()
            my_num = self.num_to_place.get()
            has_placements = num != len(persons.persons)

            if num != my_num and has_placements:
                self.controller.show_err(err_msg)
        else:
            self.controller.show_err(err_msg)
        
class SettingsPane(ttk.LabelFrame):
    def __init__(self, master, controller):
        ttk.LabelFrame.__init__(
            self, master, text='Kontroller', width=400)
        self.master = master
        self.controller = controller
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        sett = controller.prj_wrapped['settings']

        # placement buttons
        ttk.Button(self, text='Automatplacera',
            command=self.auto_place
        ).grid(row=0, column=0, sticky='nw', pady=5, padx=5)

        ttk.Button(self, text='Rensa placeringar',
            command=self.clear_placements
        ).grid(row=0, column=0, sticky='ne', pady=5, padx=5)

        # how many to place
        ttk.Label(self, text='Antal att placera'
        ).grid(row=1, column=0, sticky='w')

        spin = ttk.Spinbox(self,
            textvariable=master.num_to_place)
        spin.configure(state='disabled')
        spin.grid(row=2, column=0, sticky='wne')

        # outputs
        ttk.Label(self, text='Utdata mapp'
        ).grid(row=3, column=0, sticky='w')

        LookupPath(self, sett['output_folder'], 'dir', sett
        ).grid(row=4, column=0, stick='wne')

        # generate buttons
        btnfrm = ttk.LabelFrame(self, text='Generera')
        btnfrm.grid(row=5, columnspan=2, sticky='wne')
        
        self.card_btn = ttk.Button(btnfrm, text='Placeringskort',
            command=self.gen_placement_cards)
        self.card_btn.grid(row=0, column=0, sticky='wne', pady=5, padx=5)

        self.card_link = DocLink(btnfrm)
        self.card_link.grid(row=0, column=1, sticky='nes', pady=5, padx=5)
        
        self.list_btn = ttk.Button(btnfrm, text='Placeringslist',
            command=self.gen_placement_list)
        self.list_btn.grid(row=1, column=0, sticky='wne', pady=5, padx=5)
        
        self.list_link = DocLink(btnfrm)
        self.list_link.grid(row=1, column=1, sticky='nes', pady=5, padx=5)

        self.meal_btn = ttk.Button(btnfrm, text='Specialkostslista',
            command=self.gen_specialfoods_list)
        self.meal_btn.grid(row=2, column=0, sticky='wne', pady=5, padx=5)

        self.meal_link = DocLink(btnfrm)
        self.meal_link.grid(row=2, column=1, sticky='nes', pady=5, padx=5)

        self.master.num_to_place.trace_add(
            'write', self.set_gen_btn_state)
        self.set_gen_btn_state()

    def set_gen_btn_state(self, *args):
        num = self.master.num_to_place.get()
        state = 'disabled' if num > 0 else 'enabled'
        for ctl in (self.card_btn, self.list_btn, self.meal_btn):
            ctl.configure(state=state)

    def auto_place(self):
        prj = self.controller.project
        try:
            prj.tables.place_persons() 
        except AppException as e:
            self.controller.show_error(str(e))

        self.controller.rewrap('persons')
        self.controller.rewrap('tables')

        to_place = prj.persons.num_to_place()
        self.master.num_to_place.set(to_place)
   
    def clear_placements(self):
        ok = messagebox.askokcancel('Är du säker?',
            'Vill du verligen rensa alla placeringar?')
        if not ok:
            return
        prj = self.controller.project
        prj.tables.clear_placements()

        self.controller.rewrap('tables')
        self.controller.rewrap('persons')

        to_place = prj.persons.num_to_place()
        self.master.num_to_place.set(to_place)

    def gen_placement_cards(self):
        prj = self.controller.project
        create_name_cards(prj, prj.persons.persons)
        save_path = create_namecard_docx(prj)
        self.card_link.set_url('Placeringskort', save_path)

    def gen_placement_list(self):
        prj = self.controller.project
        save_path = create_table_report(prj)
        self.list_link.set_url('Placeringslista', save_path)

    def gen_specialfoods_list(self):
        prj = self.controller.project
        save_path = create_special_foods_report(prj)
        self.meal_link.set_url('Specialkost', save_path)

class DocLink(ttk.Label):
    _cls_init_ok = False

    @classmethod
    def _cls_init(cls):
        st = ttk.Style()
        st.configure('LinkHover.TLabel', 
            background="#9A9E9A")
        st.configure('LinkHover.TLabel', 
            foreground="#191B18")
        st.configure('Link.TLabel',
            background="#C9C8CC")
        st.configure('Link.TLabel',
            foreground="#170149")
        cls._cls_init_ok = True

    def __init__(self, master):
        if not DocLink._cls_init_ok:
            DocLink._cls_init() # run only once

        self.txt = tk.StringVar(value='')
        self.url = tk.StringVar(value='')

        ttk.Label.__init__(self, master, textvariable=self.txt)
        self.master = master

        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)

    def set_url(self, text, url):
        self.txt.set(text)
        self.url.set(Path(url).absolute())

    def on_enter(self, event):
        st = 'LinkHover.TLabel' if self.txt.get() else 'TLabel'
        self.configure(style=st)

    def on_leave(self, event):
        st = 'Link.TLabel' if self.txt.get() else 'TLabel'
        self.configure(style=st)

    def on_click(self, event):
        if self.url.get():
            webbrowser.open_new(f'file://{self.url.get()}')


class TableViewPane(ttk.LabelFrame):
    def __init__(self, master, controller):
        ttk.LabelFrame.__init__(
            self, master, text='Bordsplaceringar')
        self.master = master
        self.controller = controller

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.tbl = PlacementsTable(self, controller, master.num_to_place)
        self.tbl.grid(row=0, column=0, sticky='nsew')

        vscroll = ttk.Scrollbar(
            self, orient='vertical', command=self.tbl.yview)
        self.tbl.configure(yscrollcommand=vscroll.set)
        vscroll.grid(row=0, column=1, sticky='nes')

        # recreate when this variable changes
        self.master.num_to_place.trace_add(
            'write', self.tbl.recreate)


class PlacementsTable(ttk.Treeview):
    def __init__(self, master, controller, unplaced_var):
        cols = ('Bord', 'Person', 'Avdelning', 'Specialkost')
        ttk.Treeview.__init__(self, master, columns=cols, selectmode='none')
        self.master = master
        self.controller = controller
        self.unplaced_var = unplaced_var

        # iid to persons idx
        self.iids = {}

        # add headings
        for c in cols:
            self.heading(c, text=c)
        self.column(cols[0], width=120, minwidth=0, stretch=False)
        self.column(cols[1], width=200, minwidth=0, stretch=False)
        self.column(cols[2], width=120, minwidth=0, stretch=False)
        self.column('#0', width=20, minwidth=0, stretch=False)

        self.bind(f'<Button-3>', self.right_clicked)

        self.recreate()

    def recreate(self, *args):
        regex = re.compile(r'\s*\(.*\)$')
        opened = [regex.sub('', self.item(c)['values'][0])
            for i,c in enumerate(self.get_children())
            if self.item(c)['open']
        ]
        scroll = self.yview()
       
        self.delete(*self.get_children())
        self.iids = {}

        def ins_person(root, idx, tbl, person):
            vlus = (f'   {tbl}',
                f'{person.fname} {person.lname}',
                f'{person.dept.id}',
                f'{person.special_foods}'
            )
            iid = self.insert(root, tk.END, values=vlus)
            self.iids[iid] = idx

        tables = self.controller.project.tables
        persons = self.controller.project.persons
        to_place = persons.num_to_place()
        if to_place > 0:
            tbl = 'Oplacerade'
            root = self.insert('',tk.END, values=(tbl,))
            for i,p in enumerate(persons.persons):
                if not p.table():
                    ins_person(root, i, tbl, p)

        for i,tbl in enumerate(tables.tables):
            header = f'{tbl.id} ({tbl.free_seats()} av {tbl.num_seats})'
            root = self.insert('',tk.END, values=(header,))
            for p in tbl.persons:
                idx = persons.persons.index(p)
                ins_person(root, idx, tbl.id, p)

        # restore expanded leaves
        for ch in self.get_children():
            itm = self.item(ch)
            if regex.sub('', itm['values'][0]) in opened:
                self.item(ch, open=1)
        self.yview(tk.MOVETO, scroll[0])

        self.update()

    def person_for_event(self, event):
        iid = self.identify_row(event.y)
        col = self.identify_column(event.x)

        # bail out if it it is a table or arrow col
        if not iid or not iid in self.iids or \
           not col or col == '#0':
            return

        idx = self.iids[iid]

        persons = self.controller.project.persons.persons
        if len(persons) <= idx or idx < 0:
            return
        return persons[idx], iid, col
        
    def right_clicked(self, event):
        res = self.person_for_event(event)
        if not res:
            return
        
        person, iid, col = res
        menu = tk.Menu(self, tearoff=0)

        # form a closure
        def closure(per, func, arg):
            def inner(*args):
                func(per, arg)
            return inner

        # build up the menu
        if person.table():
            menu.add_command(label='Ta bort placering', 
                command=closure(person, self.unplace, None))
            menu.add_separator()
        
        # all tables with free places
        for tbl in self.controller.project.tables.tables:
            if tbl.free_seats() == 0:
                continue
            menu.add_command(label=f'Flytta till {tbl.id}', 
                command=closure(person, self.move_to, tbl))
        
        # popup menu
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def refresh_unplaced_var(self):
        prj = self.controller.project
        self.unplaced_var.set(prj.persons.num_to_place())
    
    def unplace(self, person, extra):
        tbl = person.table()
        if not tbl:
            return
        
        tbl.unplace_person(person)

        self.controller.rewrap('tables')
        self.controller.rewrap('persons')
        self.recreate()
        self.refresh_unplaced_var()

    def move_to(self, person, new_tbl):
        tbl = person.table()
            
        name = f'{person.fname} {person.lname}'
        if tbl and not tbl.unplace(person):
            self.controller.show_message(
                f'Kunde avplacera {name} från {tbl.id}')
            return

        if not new_tbl.place_person(person):
            self.controller.show_message(
                f'Kunde inte placera {name} vid {new_tbl.id}')
            tbl.place_person(person)
            return

        self.controller.rewrap('tables')
        self.controller.rewrap('persons')
        self.recreate()
        self.refresh_unplaced_var()
