
import tkinter as tk 
from tkinter import ttk
from tkinter import messagebox
import platform
import webbrowser

class PageHeader(ttk.Frame):
    def __init__(self, page, controller, **kwargs):
        ttk.Frame.__init__(self, page, **kwargs)
        self.controller = controller
        #self.rowconfigure(2, weight=1)
        self.grid(row=0, column=0, columnspan=2, sticky='wne')

        # undo redo buttons
        u_btn = ttk.Button(self, text='<', width=1,
            command=lambda *a:controller.event_generate('<<undo>>'))
        u_btn.grid(row=0, column=0, pady=5, padx=2, sticky='wn')
        
        r_btn = ttk.Button(self, text='>', width=1,
            command=lambda *a: controller.event_generate('<<redo>>'))
        r_btn.grid(row=0, column=1, pady=5, padx=2, sticky='wn')
        
         # page header
        lbl = ttk.Label(self, textvariable=controller.header_var, 
                        font=controller.title_font)
        lbl.grid(row=0, column=2, pady=10, padx=3, sticky='wne')

def main_menu(window, undo):
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
        command=lambda:window.event_generate('<<undo>>'),
        accelerator=f'{ctrl}+Z')
    edit.add_command(
        label='Redo', 
        command=lambda:window.event_generate('<<redo>>'),
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