import tkinter as tk
from tkinter import ttk 
from tkinter import filedialog
from pathlib import Path
from datetime import datetime
from tkcalendar import Calendar, DateEntry
from menu import PageHeader

class ProjectPage(ttk.Frame):
    name = "Projekt vy"
    def __init__(self, master, controller):
        ttk.Frame.__init__(self, master)
        self.controller = controller
        prj = self.controller.prj_wrapped
        self.settings = sett = prj['settings']
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        # page header
        PageHeader(self, controller)

        sett_pane = SettingsFrame(self, controller)
        sett_pane.columnconfigure(0, weight=0)
        sett_pane.columnconfigure(1,weight=0)
        sett_pane.rowconfigure(0, weight=1)
        sett_pane.grid(row=1, column=0, padx=5, sticky='wnes')

        cont_pane = ContentFrame(self, controller)
        cont_pane.columnconfigure(0, weight=0)
        cont_pane.columnconfigure(1, weight=2)
        cont_pane.rowconfigure(1, weight=1)
        cont_pane.grid(row=1, column=1, padx=5, sticky='wnes')

class SettingsFrame(ttk.LabelFrame):
    def __init__(self, master, controller, **kwargs):
        ttk.LabelFrame.__init__(
            self, master, text='Inställningar', **kwargs)

        sett = controller.prj_wrapped['settings']

        # project name
        prj_name_lbl = ttk.Label(self, text='Projekt namn')
        prj_name_lbl.grid(row=0, column=0, sticky='w')
        prj_name_entry = ttk.Entry(self, textvariable=sett['project_name'])
        prj_name_entry.grid(row=1, column=0, sticky='we')

        # the date for this party
        prj_date = DateTime(self, sett['date'], sett)
        prj_date.grid(row=2, column=0, sticky="we")

        # project file path
        ttk.Label(self, text='Projekt fil sökväg:')\
            .grid(row=3, column=0, sticky='w')
        prj_path = ttk.Entry(self, 
            textvariable=sett['project_file_path'],
            validate='all',
            validatecommand=lambda *a:False)
        prj_path.grid(row=4,column=0, sticky='w')

        # path to persons input file
        persons_file_lbl = ttk.Label(self, text="Personer indata fil:")
        persons_file_lbl.grid(row=5, column=0, sticky='w')
        out_folder = LookupPath(
            self, sett['persons']['file'], 'file_open', sett)
        out_folder.grid(row=6, column=0, sticky='we')

        # path to departments input file
        depts_file_lbl = ttk.Label(self, text="Avdelningar indata fil:")
        depts_file_lbl.grid(row=7, column=0, sticky='w')
        out_folder = LookupPath(
            self, sett['departments']['file'], 'file_open', sett)
        out_folder.grid(row=8, column=0, sticky='we')

        # path to departments input file
        depts_file_lbl = ttk.Label(self, text="Bord indata fil:")
        depts_file_lbl.grid(row=9, column=0, sticky='w')
        out_folder = LookupPath(
            self, sett['tables']['file'], 'file_open', sett)
        out_folder.grid(row=10, column=0, sticky='we')

        # path to output folder
        out_folder_lbl = ttk.Label(self, text="Utdata mapp:")
        out_folder_lbl.grid(row=11, column=0, sticky='w')
        out_folder = LookupPath(
            self, sett['output_folder'], 'dir', sett)
        out_folder.grid(row=12, column=0, sticky='we')

        for wgt in self.winfo_children():
            wgt.grid_configure(padx=5)


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

class DateTime(ttk.Frame):
    def __init__(self, master, variable, settings, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        self.textvariable = variable
        self.settings = settings
        var = self.textvariable.get()
        self._my_event = False

        variable.trace_add('write', self.variable_changed)

        # some trickery to separate date from time
        # could not get around that with these controls
        self.date_var = tk.StringVar(value=var[:10])
        self.hour_var = tk.StringVar(value=int(var[11:13]))
        self.min_var = tk.StringVar(value=int(var[14:16]))
        self.date_var.trace_add('write', lambda *a: self.datetime_changed())
        self.hour_var.trace_add('write', lambda *a: self.datetime_changed())
        self.min_var.trace_add('write', lambda *a: self.datetime_changed())
        
        self.cal = Calendar(self, selectmode='day',
            textvariable=self.date_var, locale='sv_SE')
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
        self._my_event = True
        self.textvariable.set(s)

    def variable_changed(self, *args):
        if not self._my_event:
            dtstr = self.textvariable.get()
            self.date_var.set(dtstr[:10])
            self.hour_var.set(dtstr[11:13])
            self.min_var.set(dtstr[14:16])

        self._my_event = False

class ContentFrame(ttk.LabelFrame):
    def __init__(self, master, controller, **kwargs):
        ttk.LabelFrame.__init__(
            self, master, text='Data', **kwargs)
        self.controller = controller

        prj = controller.prj_wrapped
        self.settings = prj['settings']

        # variable that gets chenged whenever we change indata
        self.indata = tk.StringVar(value='persons')
        self.indata.trace_add('write', self.indata_changed)

        #indata selector
        ttk.Label(self, text='Visa indata') \
            .grid(row=0, column=0, sticky='w')
        self.selector = ttk.Combobox(
            self, textvariable=self.indata,
            values=[v['name'] for _,v in self.indata_sources().items()]
        )
        self.selector.grid(row=0, column=1, sticky='w')

        # change column order
        ttk.Button(
            self, text='Ändra kolumn ordning', 
            command=self.change_col_order
        ).grid(row=0, column=2, sticky='ne')
        
        # update when file externally 
        ttk.Button(
            self, text='Läs om', 
            command=self.reload_data
        ).grid(row=0, column=3, sticky='ne')

        self.tbl = TableWidget(self, self.indata)
        self.tbl.grid(row=1, column=0, columnspan=4, sticky='wnes')
        
        # scrollbars
        vscroll = ttk.Scrollbar(self, orient='vertical', command=self.tbl.yview)
        self.tbl.configure(yscrollcommand=vscroll.set)
        vscroll.grid(row=1, column=3, sticky='nes')

        hscroll = ttk.Scrollbar(self, orient='horizontal', command=self.tbl.xview)
        self.tbl.configure(xscrollcommand=hscroll.set)
        hscroll.grid(row=2, column=0, columnspan=4, sticky='wne')

        controller.bind('<<Reloaded>>', lambda *a: self.tbl.recreate())
        controller.bind('<<IndataReloaded>>', self.indata_reloaded)

    def indata_sources(self):
        prj = self.controller.prj_wrapped
        sett = self.settings
        return  {
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
    
    def indata_key(self):
        sel = self.indata.get()
        key = next(k for k,v in self.indata_sources().items()
                   if k == sel or v['name'] == sel)
        return key

    def indata_changed(self, *args):
        source = self.indata.get()
        print(source)
    
    def change_col_order(self, *args):
        ColumnOrderDlg(self, self.controller)
        self.reload_data()

    def reload_data(self, *args):
        try:
            self.controller.reload(
                self.indata_key())
            self.tbl.recreate()
        except Exception:
            pass

    def indata_reloaded(self, event):
        key = self.indata_key()
        if self.controller.last_indata_change == key:
            self.tbl.recreate()

class TableWidget(ttk.Treeview):
    def __init__(self, master, indatavar, **kwargs):
        ttk.Treeview.__init__(self, master, show=['headings'], **kwargs)
        self.indatavar = indatavar
        indatavar.trace_add('write', lambda *a: self.recreate())
        self.recreate()

    def recreate(self):
        self.delete(*self.get_children())
        self['columns'] = ()

        name = self.indatavar.get()
        indata_sources = self.master.indata_sources()
        for k,v in indata_sources.items():
            if v['name'] == name:
                return self._recreate(v['obj'], k, v['hdrs'], v['specialcols'])
            
        k,v = 'persons', indata_sources['persons']
        self._recreate(v['obj'], k, v['hdrs'], v['specialcols'])

    def _recreate(self, obj, key, hdrs, specialcols):
        hdr_names = obj['_data'].headers \
            if obj and hasattr(obj, '_data') else [k for k in hdrs.keys()]
        conf_hdrs = {k:v.get() for k,v in self.master.controller\
                        .prj_wrapped['settings'][key]['hdrs'].items()}
        hdr_keys = {v:k for k,v in conf_hdrs.items()}
        rows = obj[key] if obj else ()

        # rows from here on
        def get_col(idx, row):
            if len(hdrs) <= idx:
                return None
            key = hdr_keys[idx]
            return specialcols[key](row) \
                if key in specialcols else row[key].get()

        insert_rows = []
        col_max = max(len(hdr_names), len(hdrs))

        # generate cols in mem before insert to get the max column count
        for row in rows:
            vlus = []
            for i,_ in enumerate(hdr_names):
                vlu = get_col(i, row)
                if isinstance(vlu, list):
                    vlus.extend(vlu)
                else:
                    vlus.append(vlu)

            col_max = max(col_max, len(vlus))
            insert_rows.append(vlus)

        # columns 
        # a row can be a list, extend to added columns
        self['columns'] = [i for i in range(col_max)]

        # name columns and insert them
        for i in range(col_max):
            hidx,hd = next(((k,v) for idx, (k,v) in enumerate(hdr_keys.items())
                       if idx == i), (i,'?'))
            h = hdr_names[hidx] if hidx < len(hdr_names) \
                else f'{hdr_names[-1]}-{hidx - len(hdr_names)+1}'
            s = f'{hd} ({h})' if h != hd else f'{h}'
            self.heading(i, text=s)
            self.column(i, width=120, minwidth=0, stretch=False)

        # lastly insert the rows
        for vlus in insert_rows:
            self.insert('', tk.END, values=vlus)

        self.update()

class ColumnOrderDlg(tk.Toplevel):
    def __init__(self, master, controller, **args):

        # get background from root window
        s = ttk.Style()
        bg = s.lookup('TFrame', 'background')

        tk.Toplevel.__init__(
            self, master, takefocus=True, bg=bg, **args)
        
        self.master = master
        self.controller = controller

        # header
        ttk.Label(
            self, text='Ändra kolumn ordning',
            font=controller.title_font
        ).grid(row=0, column=0, columnspan=2,
            sticky='nwe', pady=5, padx=5)

        sel = self.master.indata.get()

        # what table are we changing?
        src = master.indata_sources()[master.indata_key()]
        self.headers = ['']
        self.headers.extend([h for h in src['obj']['_data'].headers])

        self.vars = {}
        # insert selections
        i = 1
        for col, idx in src['hdrs'].items():
            lbl =ttk.Label(self, text=col)
            lbl.grid(row=i,column=0, sticky='w', pady=5, padx=5)

            var = tk.StringVar(
                self, value=self.headers[src['hdrs'][col].get()+1])
            self.vars[col] = var
            var.trace_add('write', self.col_changed)

            cmb = ttk.Combobox(self, values=self.headers, textvariable=var)
            cmb.grid(row=i, column=1, sticky='we', pady=5, padx=5)
            i += 1

        ttk.Button(
            self, text='Avbryt', command=self.destroy
        ).grid(row=i, column=0, sticky='w', padx=5, pady=5)
        self.ok = ttk.Button(
            self, text='OK', command=self.accept)
        self.ok.grid(row=i, column=1, sticky='e', padx=5, pady=5)

        self.ok_btn_state()

        # make this dialog modal
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.transient(master)
        self.wait_visibility()
        self.grab_set()
        self.wait_window()

    def col_changed(self, var_id, b, method):
        var = next(v for _,v in self.vars.items() 
                   if str(v) == var_id)
        new_vlu = var.get()
        if not new_vlu:
            self.ok_btn_state()
            return # ignore empty selection
        
        for _,v in self.vars.items():
            if v is var:
                continue # ignore as this is me
            if v.get() == new_vlu:
                v.set('')
        
        self.ok_btn_state()

    def is_all_selected(self):
        for _,v in self.vars.items():
            if not v.get():
                return False
        return True
    
    def ok_btn_state(self):
        str = 'normal' if self.is_all_selected() else 'disabled'
        self.ok.configure(state=str)

    def accept(self):
        sel = self.master.indata_key()
        tbl = self.controller.prj_wrapped['settings'][sel]
        hdrs = tbl['hdrs']
        self.headers.pop(0)

        for col, idx in hdrs.items():
            new_vlu = self.headers.index(self.vars[col].get())
            old_vlu = hdrs[col].get()
            if new_vlu != old_vlu:
                hdrs[col].set(new_vlu)
        
        self.destroy()
