
import tkinter as tk 
from tkinter import ttk
from tkinter import messagebox
import platform
import webbrowser
from undo_redo import Undo

class PageHeader(ttk.Frame):
    def __init__(self, page, controller, **kwargs):
        ttk.Frame.__init__(self, page, **kwargs)
        self.controller = controller
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.grid(row=0, column=0, columnspan=2, sticky='wne')

        # undo redo buttons
        u_btn = ttk.Button(self, text='<', width=1,
            command=lambda *a: Undo.ref().undo())
        u_btn.grid(row=0, column=0, pady=5, padx=2, sticky='wn')
        
        r_btn = ttk.Button(self, text='>', width=1,
            command=lambda *a: Undo.ref().redo())
        r_btn.grid(row=0, column=1, pady=5, padx=2, sticky='wn')
        
         # page header
        lbl = ttk.Label(self, textvariable=controller.header_var, 
                        font=controller.title_font)
        lbl.grid(row=0, column=2, pady=10, padx=3, sticky='wne')

        # error messages view
        self.msgs = MessagesView(self, controller)
        self.msgs.grid(row=0, columns=3, sticky='nesw')

# we use a canvas as warapper here to 
# make a scrollable area
class MessagesView(tk.Canvas):
    def __init__(self, master, controller):
        style = ttk.Style()
        bg = style.lookup('TFrame','background')
        tk.Canvas.__init__(self, master, 
            width=400, height=50, bg=bg, 
            highlightthickness=0)
        self.master = master
        self.controller = controller

        self.grid(row=0, column=3, sticky='en', padx=5)
        
        # the content frame
        self.frm = ttk.Frame(self, width=self.winfo_width(), height=0) 
        self.frm.columnconfigure(0, weight=1)
        self.create_window((0,0), window=self.frm, anchor='nw')

        # scroll stuff
        def frm_changed(event):
            frm_h = self.frm.winfo_height()
            my_h = self.winfo_height()
            if frm_h < my_h:
                if self.scroll:
                    self.scroll.destroy()
                    self.scroll = None                
                    self.configure(yscrollcommand=lambda *a: None)
                    self.after(100, 
                        lambda *a:self.yview_moveto(0))
            elif not self.scroll:
                self.scroll = ttk.Scrollbar(master, orient='vertical', command=self.yview)
                self.configure(yscrollcommand=self.scroll.set)
                self.scroll.grid(row=0, column=4, sticky='nes')

            if self.scroll:
                self.configure(scrollregion=self.bbox('all'))
        
        # add scoll when a widget is added
        self.scroll = None
        self.frm.bind('<Configure>', frm_changed) 

        # style messages
        style = ttk.Style()
        style.configure('sMsgError.TEntry', fieldbackground="#f5bdc2")
        style.configure('sMsgError.TEntry', foreground="#6C0909")
        style.configure('sMsg.TEntry', fieldbackground="#EAFAE1")
        style.configure('sMsg.TEntry', foreground="#084C16")

    def add_message(self, text):
        Message(self, text)

    def add_error(self, text):
        Message(self, text, True)

class Message(ttk.Frame):
    def __init__(self, master, text, is_error=False):
        ttk.Frame.__init__(self, master.frm, width=master.winfo_width())
        self.master = master
        self.columnconfigure(0, weight=1)
        self.grid(column=0, sticky='we')

        id = 'sMsgError' if is_error else 'sMsg'

        # messagebox, wrap in a Frame to be able to specify 
        # width height explicitly
        master_w, frm_h = master.winfo_width(), 20
        frm = ttk.Frame(self, width=master_w, height=frm_h)

        txt = ttk.Entry(frm, style=f'{id}.TEntry')
        txt.insert(0, text)
        txt.configure(validate='all')
        txt.configure(validatecommand=lambda *a:False)

        close = CloseBtn(self, command=self.close)

        txt_w = master_w - 25
        txt.place(x=0,y=0, width=txt_w, height=20)
        close.place(x=txt_w, y=0)

        frm.grid(row=0, column=0, sticky='we')
        frm.grid_propagate(False)

        self.after(100, 
            lambda *a:self.master.yview_moveto(1))

    def close(self, *args):
        self.destroy()

class CloseBtn(ttk.Label):
    _init_styles = False

    @classmethod
    def _cls_init(cls):
        # only configure styles once
        cls._init_styles = True
        style = ttk.Style()
        style.configure('sClose.TLabel', background="#888787")
        style.configure('sClose.TLabel', foreground='#3A0101')
        style.configure('sClose.TLabel', bordercolor="#494848")
        style.configure('sClose.TLabel', borderwidth=1)

    def __init__(self, master, **kwargs):
        command = kwargs.pop('command', None)
        if not hasattr(kwargs, 'text'):
            kwargs['text'] = '✖'
        if not hasattr(kwargs, 'style'):
            kwargs['style'] = 'sClose.TLabel'

        if not CloseBtn._init_styles:
            CloseBtn._cls_init()

        ttk.Label.__init__(self, master, **kwargs)

        self.sCloseHover = ttk.Style()
        self.sCloseHover.configure('sCloseHover.TLabel', background='#3A0101')
        self.sCloseHover.configure('sCloseHover.TLabel', foreground='#958989')
        self.sCloseHover.configure('sCloseHover.TLabel', bordercolor='#CCCCCC')
        self.sCloseHover.configure('sCloseHover.TLabel', borderwidth=1)
        self.bind('<Enter>', 
            lambda e: self.configure(style='sCloseHover.TLabel'))
        self.bind('<Leave>', 
            lambda e: self.configure(style='sClose.TLabel'))

        if command:
            self.bind('<Button-1>', lambda e: command())

def main_menu(window):
    # Creating Menubar
    menubar = tk.Menu(window)
    # Adding File Menu and commands
    ctrl = 'Command' if platform == 'darwin' else 'Control'
    file = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label ='Arkiv', menu=file)
    file.add_command(label ='Nytt project', command=None)
    file.add_command(
        label ='Öppna...', 
        command=window.open,
        accelerator=f'{ctrl}+O')
    file.add_command(
        label ='Spara', 
        command=window.save,
        accelerator=f'{ctrl}+S')
    file.add_command(
        label ='Spara som', 
        command=window.save_as,
        accelerator=f'{ctrl}+Shift+S')
    file.add_separator()
    file.add_command(label ='Avsluta', command=window.destroy)

    # Adding Edit Menu and commands
    edit = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label ='Redigera', menu=edit)
    edit.add_command(
        label='Undo', 
        command=lambda: Undo.ref().undo(),
        accelerator=f'{ctrl}+Z')
    edit.add_command(
        label='Redo', 
        command=lambda: Undo.ref().redo(),
        accelerator=f'{ctrl}+Shift+Z')
    edit.add_separator()
    edit.add_command(label ='Find...', command=None)
    edit.add_command(label ='Find again', command=None)

    # Adding Help Menu
    help_ = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label ='Hjälp', menu=help_)
    help_.add_command(label ='Om programmet', command=about)
    help_.add_command(label ='Kort hjälp', command=helpdialog)
    help_.add_command(
        label ='Readme',
        command=lambda:webbrowser.open('https://github.com/mumme74/party_scripts/'))
    help_.add_separator()
    help_.add_command(
        label ='Om Tk',
        command=lambda:webbrowser.open('https://tkdocs.com/shipman/'))

    window.config(menu = menubar)

def about(*args):
    msg = '''
    Denna app är till för att enkelt kunna skapa brodsplaceringar 
    i stora sällskap. Som personalfester, bröllop, och andra träffar.

    Det skapar bordsplaceringar där folk får sitta tillsammans
    med sin avdelning (sitt arbetslag) i möjligaste mån.

    Den har sin grund i ett snabbt ihopsatt program som 
    jag skapade då mitt arbetslag skulle organisera 
    personalfesten sommaren 2025 för 156 personer
    '''
    messagebox.showinfo('Om appen', msg)

def helpdialog(*args):
    msg = '''
    En mer lättläslig info finns på projektets README sida:
      https://github.com/mumme74/party_scripts
 
    Som indata användas vanliga filer som:
      * excell kalkylark (xlsx), 
      * tabbseparerad (tsv), 
      * Semikolon separerad (csv) 
      * samt json (dataexporterings format). 

    Tanken är att man i första hand samlar in indata på annat vis.
    T.ex. via tex ett webbformulär. sparar ned data i rätt format.
    Personfilen bör/skall ha kolumner för:
      * registeringsdatum
      * epost
      * förnamn
      * efternamn
      * avdelning
      * specialkost
    Helst i den ordningen

    Därefter skapa en bordsfil med antal platser per bord.

    Sedan skapar man en fil med vilka avdelningar som finns och 
    synonymer som folk kan ha skrivit. 
    Om insamlingsformuläret har haft fritext kan man ange 
    godtycklig antal synonymer för att matcha rätt.
    Skall ha kolumner:
      * förkortning
      * namn
      * synonymer 
      *  (en kolumn per ytterligare synonym) ...

    När persondata läses in matchas den mot ovan. 
    VERSALER och gemener spelar ingen roll.
    '''
    messagebox.showinfo('Hjälp', msg)