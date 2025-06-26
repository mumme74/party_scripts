import tkinter as tk
from tkinter import ttk 
from tkinter import messagebox
from menu import PageHeader
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

        # keep track of how many people to place
        to_place = prj.persons.num_to_place()
        self.num_to_place = tk.IntVar(value=to_place)

        SettingsPane(self, controller
        ).grid(row=1, column=0, sticky='nw', padx=5, pady=5)

        
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
        
        self.list_btn = ttk.Button(btnfrm, text='Placeringslist',
            command=self.gen_placement_list)
        self.list_btn.grid(row=1, column=0, sticky='wne', pady=5, padx=5)
        
        self.meal_btn = ttk.Button(btnfrm, text='Specialkostslista',
            command=self.gen_specialfoods_list)
        self.meal_btn.grid(row=2, column=0, sticky='wne', pady=5, padx=5)

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
        to_place = prj.persons.num_to_place()
        self.master.num_to_place.set(to_place)
   
    def clear_placements(self):
        ok = messagebox.askokcancel('Är du säker?',
            'Vill du verligen rensa alla placeringar?')
        if not ok:
            return
        prj = self.controller.project
        prj.tables.clear_placements()
        to_place = prj.persons.num_to_place()
        self.master.num_to_place.set(to_place)

    def gen_placement_cards(self):
        prj = self.controller.project
        create_name_cards(prj, prj.persons)
        create_namecard_docx(prj)

    def gen_placement_list(self):
        prj = self.controller.project
        create_table_report(prj)

    def gen_specialfoods_list(self):
        prj = self.controller.project
        create_special_foods_report(prj)
