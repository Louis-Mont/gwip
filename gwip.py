from tkinter import END, Tk, Entry, StringVar, Label, RAISED, Button, OptionMenu, Text, Scrollbar
from gw_logging.Log import Log
from Core.Core import Core

VERSION = '1.4.0 EXPERIMENTAL'

cats = ['Meubles', 'Electroménagers', 'Multimédias', 'Textile', 'Culture', 'Loisirs', 'Vaisselle',
        'Bricolage-Jardinage',
        'Décoration-Bibelot', 'Puériculture']

PS_DB = None
GDR_DB = None
C = None


def main():
    prestashop_ip = ps_ip.get()
    prestashop_login = ps_login.get()
    prestashop_pwd = ps_password.get()
    prestashop_db_name = ps_db_entry.get()
    dsn = gdr_dsn.get()

    PS_DB, GDR_DB = C.connect(gdr_dsn.get(), ps_ip.get(), ps_login.get(), ps_password.get(), ps_db_entry.get())
    return PS_DB, GDR_DB


def on_closing(dbs, names):
    """
    When the main frame closes
    :param dbs: databases to be closed
    :param names: names of the databases, purely for logs
    """
    for i in range(len(dbs)):
        if dbs[i] is not None:
            dbs[i].close()
        print(f"{names[i]} database connection correctly closed")

    frame.destroy()


if __name__ == "__main__":
    frame = Tk()
    frame.title(f"GDR to Prestashop V{VERSION}")
    frame.minsize(400, 300)
    # cols
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)
    frame.columnconfigure(2, weight=1)
    frame.columnconfigure(3, weight=1)
    # rows
    frame.rowconfigure(0, weight=1)
    frame.rowconfigure(1, weight=1)
    frame.rowconfigure(2, weight=1)
    frame.rowconfigure(3, weight=1)
    frame.rowconfigure(4, weight=1)
    frame.rowconfigure(5, weight=4)
    # items
    ps_ip = Entry(frame)
    ps_ip.insert(0, '127.0.0.1')
    ps_ip.insert(END, '')
    ps_ip.grid(row=0, column=1)

    ps_ip_text = StringVar()
    ps_ip_text.set("IP Prestashop")
    ps_ip_label = Label(frame, textvariable=ps_ip_text, relief=RAISED)
    ps_ip_label.grid(row=0, column=0)

    ps_db_entry = Entry(frame)
    ps_db_entry.insert(0, 'prestashop')
    ps_db_entry.insert(END, '')
    ps_db_entry.grid(row=1, column=1)

    ps_db_text = StringVar()
    ps_db_text.set("Nom de la base de données")
    ps_db_label = Label(frame, textvariable=ps_db_text, relief=RAISED)
    ps_db_label.grid(row=1, column=0)

    ps_login = Entry(frame)
    ps_login.insert(0, 'root')
    ps_login.insert(END, '')
    ps_login.grid(row=2, column=1)

    ps_login_text = StringVar()
    ps_login_text.set("Login BDD Prestashop")
    ps_login_label = Label(frame, textvariable=ps_login_text, relief=RAISED)
    ps_login_label.grid(row=2, column=0)

    ps_password = Entry(frame)
    ps_password.insert(0, '')
    ps_password.insert(END, '')
    ps_password.grid(row=3, column=1)

    ps_password_text = StringVar()
    ps_password_text.set("Mdp BDD Prestashop")
    ps_password_label = Label(
        frame, textvariable=ps_password_text, relief=RAISED)
    ps_password_label.grid(row=3, column=0)

    gdr_id = Entry(frame)
    gdr_id.insert(0, '0')
    gdr_id.insert(END, '')
    gdr_id.grid(row=0, column=3)

    gdr_id_text = StringVar()
    gdr_id_text.set("ID du produit")
    gdr_id_label = Label(frame, textvariable=gdr_id_text, relief=RAISED)
    gdr_id_label.grid(row=0, column=2)

    ps_cat_def = StringVar()
    ps_cat_def.set(cats[0])
    ps_cat_om = OptionMenu(frame, ps_cat_def, *cats)
    ps_cat_om.grid(row=1, column=3)

    ps_cat_text = StringVar()
    ps_cat_text.set("Catégorie prestashop")
    ps_cat_label = Label(frame, textvariable=ps_cat_text, relief=RAISED)
    ps_cat_label.grid(row=1, column=2)

    gdr_dsn = Entry(frame)
    gdr_dsn.insert(0, 'gdr')
    gdr_dsn.insert(END, '')
    gdr_dsn.grid(row=2, column=3)

    gdr_dsn_text = StringVar()
    gdr_dsn_text.set("DSN")
    gdr_dsn_label = Label(frame, textvariable=gdr_dsn_text, relief=RAISED)
    gdr_dsn_label.grid(row=2, column=2)

    ps_title_text = StringVar()
    ps_title_text.set("Titre")
    ps_title_label = Label(frame, textvariable=ps_title_text, relief=RAISED)
    ps_title_label.grid(row=4, column=0)

    # Title of the product on prestashop written by the user
    ps_title = Entry(frame)
    ps_title.insert(0, '')
    ps_title.insert(END, '')
    ps_title.grid(row=4, column=1)

    log = Text(frame, wrap='word')
    log.insert(END, 'Logs :')
    log.configure(state='disabled')
    log.grid(row=5, column=0, columnspan=4)
    i_log = Log(log)

    log_scroll = Scrollbar(frame, command=log.yview)
    log_scroll.grid(row=5, column=3, sticky='nse')
    log['yscrollcommand'] = log_scroll.set

    btn_addid = Button(frame, text='Add',
                       command=lambda: C.add_id(int(gdr_id.get()), ps_cat_def.get(), ps_title.get(), main()))
    btn_addid.grid(row=3, column=2)

    btn_resetdb = Button(frame, text='Reset DB', command=lambda: C.reset_db(main()))
    btn_resetdb.grid(row=3, column=3)

    btn_syncventes = Button(
        frame, text='Synchroniser Ventes', command=lambda: C.syncventes(main()))
    btn_syncventes.grid(row=4, column=2)

    C = Core(i_log, frame)
    # btn_resetdb.grid_remove()
    frame.protocol("WM_DELETE_WINDOW", lambda: on_closing(
        [PS_DB, GDR_DB], ['Prestashop', 'GDR']))
    frame.mainloop()

    input("Press any key to quit...")
