import tkinter as tk
from tkinter import ttk 
from tkinter import filedialog
from pathlib import Path
from datetime import datetime
from tkcalendar import Calendar, DateEntry
from menu import PageHeader

class ProjectPage(ttk.Frame):
    name = "Projekt vy"
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        prj = self.controller.prj_wrapped
        self.settings = sett = prj['settings']

        # page header
        PageHeader(self, controller)

        # content splitter
        pane = ttk.PanedWindow(self, orient='horizontal')
        pane.grid(row=1, column=0, padx=3, sticky="wnes")
        pane.columnconfigure(0, weight=0)
        pane.columnconfigure(1, weight=1)
        pane.rowconfigure(0, weight=1)

        SettingsFrame(pane, controller, width=300)
        ContentFrame(pane, controller)
        

class SettingsFrame(ttk.LabelFrame):
    def __init__(self, parent, controller, **kwargs):
        ttk.LabelFrame.__init__(
            self, parent, text='Inställningar', **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky='wnes')

        sett = controller.prj_wrapped['settings']

        # project name
        prj_name_lbl = ttk.Label(self, text='Projekt namn')
        prj_name_lbl.grid(row=0, column=0, sticky='w')
        prj_name_entry = ttk.Entry(self, textvariable=sett['project_name'])
        prj_name_entry.grid(row=0, column=1, sticky='we')

        # the date for this party
        ttk.Label(self, text='Datum och tid')\
            .grid(row=1, column=0, sticky='wn')
        prj_date = DateTime(self, sett['date'], sett)
        prj_date.grid(row=1, column=1, sticky="we")

        # project file path
        ttk.Label(self, text='Projekt fil sökväg:')\
            .grid(row=2, column=0, sticky='w')
        prj_path = ttk.Entry(self, 
            textvariable=sett['project_file_path'])
        prj_path.state(['disabled'])
        prj_path.grid(row=2,column=1, sticky='w')

        # path to persons input file
        persons_file_lbl = ttk.Label(self, text="Personer indata fil:")
        persons_file_lbl.grid(row=3, column=0, sticky='w')
        out_folder = LookupPath(
            self, sett['persons']['file'], 'file_open', sett)
        out_folder.grid(row=3, column=1, sticky='we')

        # path to departments input file
        depts_file_lbl = ttk.Label(self, text="Avdelningar indata fil:")
        depts_file_lbl.grid(row=4, column=0, sticky='w')
        out_folder = LookupPath(
            self, sett['departments']['file'], 'file_open', sett)
        out_folder.grid(row=4, column=1, sticky='we')

        # path to departments input file
        depts_file_lbl = ttk.Label(self, text="Bord indata fil:")
        depts_file_lbl.grid(row=5, column=0, sticky='w')
        out_folder = LookupPath(
            self, sett['tables']['file'], 'file_open', sett)
        out_folder.grid(row=5, column=1, sticky='we')

        # path to output folder
        out_folder_lbl = ttk.Label(self, text="Utdata mapp:")
        out_folder_lbl.grid(row=6, column=0, sticky='w')
        out_folder = LookupPath(
            self, sett['output_folder'], 'dir', sett)
        out_folder.grid(row=6, column=1, sticky='we')

        for wgt in self.winfo_children():
            wgt.grid_configure(padx=5, pady=5)


class LookupPath(ttk.Frame):
    def __init__(self, parent, variable, type, 
                 settings, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
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

class DateTime(ttk.Frame):
    def __init__(self, parent, variable, settings, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        self.textvariable = variable
        self.settings = settings
        var = self.textvariable.get()


        # some trickery to separate date from time
        # could not get around that with these controls
        self.date_var = tk.StringVar(value=var[:10])
        self.hour_var = tk.StringVar(value=int(var[11:13]))
        self.min_var = tk.StringVar(value=int(var[14:16]))
        self.date_var.trace_add('write', lambda *a: self.datetime_changed())
        self.hour_var.trace_add('write', lambda *a: self.datetime_changed())
        self.min_var.trace_add('write', lambda *a: self.datetime_changed())
        
        self.cal = Calendar(self, selectmode='day',
            textvariable=self.date_var, locale='sv_SE',
            #background="black", disabledbackground="black", bordercolor="black", 
            #headersbackground="black", normalbackground="black", foreground='white', 
            #normalforeground='white', headersforeground='white'
        )
        self.cal.grid(row=1, column=0, columnspan=3)
        
        self.cal.strptime(var[:10], '%Y-%m-%d')
        self.cal.bind('<<CalendarSelected>>', 
                      lambda *a: self.datetime_changed())
      
        ttk.Label(self, text='Tid: ').grid(row=0, column=0, sticky='wn')
        ttk.Spinbox(
            self, textvariable=self.hour_var, 
            from_=0, to=23, width=2) \
        .grid(
            row=0, column=1, sticky='w')   
        ttk.Spinbox(
            self, textvariable=self.min_var, 
            from_=0, to=59, width=2) \
        .grid(
            row=0, column=2, sticky='w')
        self.columnconfigure(2, weight=1)

    def datetime_changed(self):
        date = self.date_var.get()
        hour = self.hour_var.get()
        min = self.min_var.get()
        if not hour or not min:
            return
        s = f'{date} {hour}:{min}:00'
        self.textvariable.set(s)
        

class ContentFrame(ttk.LabelFrame):
    def __init__(self, parent, controller, **kwargs):
        ttk.LabelFrame.__init__(
            self, parent, text='Data', **kwargs)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self.grid(row=0, column=1, sticky='wnes')
        prj = controller.prj_wrapped
        sett = self.settings = prj['settings']

        # variable that gets chenged whenever we change indata
        self.indata = tk.StringVar(value='persons')
        self.indata.trace_add('write', lambda *a: self.indata_changed())

        # indata sources
        self.indata_sources = {
            'persons': {
                'name':'Personer', 
                'obj':prj['persons'],
                'hdrs':sett['persons']['hdrs'],
                'specialcols':{
                    'date': lambda row: row['registered_date'].get(),
                    'dept': lambda row: row['dept']['id'].get()
                }
            },
            'departments': {
                'name':'Avdelningar', 
                'obj':prj['departments'],
                'hdrs':sett['departments']['hdrs'],
                'specialcols':{
                    'syn':lambda r: [v.get() for v in r['synonyms'] if v is not None]
                }
            },
            'tables':{
                'name':'Bord',
                'obj':prj['tables'],
                'hdrs':sett['tables']['hdrs'],
                'specialcols':{
                    'prio_dept':lambda r: [v['id'].get() for v in r['prio_dept'] if v is not None]
                }
            }
        }

        #indata selector
        ttk.Label(self, text='Visa indata') \
            .grid(row=0, column=0, sticky='wn')
        selector = ttk.Combobox(
            self, textvariable=self.indata,
            values=[v['name'] for _,v in self.indata_sources.items()]
        ).grid(row=0, column=1, sticky='wn')

        tbl = TableWidget(self, self.indata)
        tbl.grid(row=1, column=0, columnspan=2, sticky='wnes')
        
        # scrollbars
        vscroll = ttk.Scrollbar(self, orient='vertical', command=tbl.yview)
        tbl.configure(yscrollcommand=vscroll.set)
        vscroll.grid(row=1, column=1, sticky='nes')

        hscroll = ttk.Scrollbar(self, orient='horizontal', command=tbl.xview)
        tbl.configure(xscrollcommand=hscroll.set)
        hscroll.grid(row=2, column=0, columnspan=2, sticky='wne')

    def indata_changed(self):
        source = self.indata.get()
        print(source)

class TableWidget(ttk.Treeview):
    def __init__(self, parent, indatavar, **kwargs):
        ttk.Treeview.__init__(self, parent, show=['headings'], **kwargs)
        self.indatavar = indatavar
        indatavar.trace_add('write', lambda *a: self.recreate())
        self.recreate()

    def recreate(self):
        self.delete(*self.get_children())
        self['columns'] = ()

        name = self.indatavar.get()
        for k,v in self.master.indata_sources.items():
            if v['name'] == name:
                return self._recreate(v['obj'], k, v['hdrs'], v['specialcols'])
            
        k,v = 'persons', self.master.indata_sources['persons']
        self._recreate(v['obj'], k, v['hdrs'], v['specialcols'])

    def _recreate(self, obj, key, hdrs, specialcols):
        obj_hdrs = obj['_data'].headers
        hdr_keys = tuple(hdrs.keys())
        self['columns'] = [i for i in range(max(len(obj_hdrs), len(hdrs)))]
        for i, h in enumerate(obj_hdrs):
            hd = next((k for k,x in hdrs.items() 
                       if x.get()==i), '?')
            s = f'{h} ({hd:.10})' if h != hd else f'{h}'
            self.heading(i, text=s)
            self.column(i, width=80, minwidth=0, stretch=False)

        def get_col(idx, row):
            if len(hdrs) <= idx:
                return None
            key = hdr_keys[idx]
            return specialcols[key](row) \
                if key in specialcols else row[key].get()

        for row in obj[key]:
            vlus = [v for v in [get_col(i, row) \
                                for i,_ in enumerate(obj_hdrs)] \
                        if v is not None]
            self.insert('', tk.END, values=vlus)

        self.update()

        

        

        
