from tkinter import Entry, END, StringVar, Label, RAISED, OptionMenu, Text, Scrollbar, Button


class Ui:
    cats = ['Meubles', 'Electroménagers', 'Multimédias', 'Textile', 'Culture', 'Loisirs', 'Vaisselle',
            'Bricolage-Jardinage',
            'Décoration-Bibelot', 'Puériculture']

    def __init__(self, frame, version):
        self.frame = frame
        frame.title(f"GDR to Prestashop v{version}")
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
        self.ps_ip = ps_ip

        ps_ip_text = StringVar()
        ps_ip_text.set("IP Prestashop")
        ps_ip_label = Label(frame, textvariable=ps_ip_text, relief=RAISED)
        ps_ip_label.grid(row=0, column=0)
        self.ps_ip_label = ps_ip_label

        ps_db_entry = Entry(frame)
        ps_db_entry.insert(0, 'prestashop')
        ps_db_entry.insert(END, '')
        ps_db_entry.grid(row=1, column=1)
        self.ps_db_entry = ps_db_entry

        ps_db_text = StringVar()
        ps_db_text.set("Nom de la base de données")
        ps_db_label = Label(frame, textvariable=ps_db_text, relief=RAISED)
        ps_db_label.grid(row=1, column=0)
        self.ps_db_label = ps_db_label

        ps_login = Entry(frame)
        ps_login.insert(0, 'root')
        ps_login.insert(END, '')
        ps_login.grid(row=2, column=1)
        self.ps_login = ps_login

        ps_login_text = StringVar()
        ps_login_text.set("Login BDD Prestashop")
        ps_login_label = Label(frame, textvariable=ps_login_text, relief=RAISED)
        ps_login_label.grid(row=2, column=0)
        self.ps_login_label = ps_login_label

        ps_password = Entry(frame)
        ps_password.insert(0, '')
        ps_password.insert(END, '')
        ps_password.grid(row=3, column=1)
        self.ps_password = ps_password

        ps_password_text = StringVar()
        ps_password_text.set("Mdp BDD Prestashop")
        ps_password_label = Label(
            frame, textvariable=ps_password_text, relief=RAISED)
        ps_password_label.grid(row=3, column=0)
        self.ps_password_label = ps_password_label

        gdr_id = Entry(frame)
        gdr_id.insert(0, '0')
        gdr_id.insert(END, '')
        gdr_id.grid(row=0, column=3)
        self.gdr_id = gdr_id

        gdr_id_text = StringVar()
        gdr_id_text.set("ID du produit")
        gdr_id_label = Label(frame, textvariable=gdr_id_text, relief=RAISED)
        gdr_id_label.grid(row=0, column=2)
        self.gdr_id_label = gdr_id_label

        ps_cat_def = StringVar()
        ps_cat_def.set(self.cats[0])
        ps_cat_om = OptionMenu(frame, ps_cat_def, *self.cats)
        ps_cat_om.grid(row=1, column=3)
        self.ps_cat_def = ps_cat_def

        ps_cat_text = StringVar()
        ps_cat_text.set("Catégorie prestashop")
        ps_cat_label = Label(frame, textvariable=ps_cat_text, relief=RAISED)
        ps_cat_label.grid(row=1, column=2)
        self.ps_cat_label = ps_cat_label

        gdr_dsn = Entry(frame)
        gdr_dsn.insert(0, 'gdr')
        gdr_dsn.insert(END, '')
        gdr_dsn.grid(row=2, column=3)
        self.gdr_dsn = gdr_dsn

        gdr_dsn_text = StringVar()
        gdr_dsn_text.set("DSN")
        gdr_dsn_label = Label(frame, textvariable=gdr_dsn_text, relief=RAISED)
        gdr_dsn_label.grid(row=2, column=2)
        self.gdr_dsn_label = gdr_dsn_label

        ps_title_text = StringVar()
        ps_title_text.set("Titre")
        ps_title_label = Label(frame, textvariable=ps_title_text, relief=RAISED)
        ps_title_label.grid(row=4, column=0)
        self.ps_title_label = ps_title_label

        # Title of the product on prestashop written by the user
        ps_title = Entry(frame)
        ps_title.insert(0, '')
        ps_title.insert(END, '')
        ps_title.grid(row=4, column=1)
        self.ps_title = ps_title

        log = Text(frame, wrap='word')
        log.insert(END, 'Logs :')
        log.configure(state='disabled')
        log.grid(row=5, column=0, columnspan=4)
        self.log = log

        log_scroll = Scrollbar(frame, command=log.yview)
        log_scroll.grid(row=5, column=3, sticky='nse')
        log['yscrollcommand'] = log_scroll.set

        btn_addid = Button(frame, text='Add', bg='lawn green')
        btn_addid.grid(row=3, column=2)
        self.btn_addid = btn_addid

        btn_resetdb = Button(frame, text='Reset DB')
        btn_resetdb.grid(row=3, column=3)
        self.btn_resetdb = btn_resetdb

        btn_syncventes = Button(
            frame, text='Synchroniser Ventes', bg='orange')
        btn_syncventes.grid(row=4, column=2)
        self.btn_syncventes = btn_syncventes

    def change_to_api_ui(self):
        ps_dir_text = StringVar()
        ps_dir_text.set("Clé Webservice")
        self.ps_db_label.configure(textvariable=ps_dir_text)
        self.ps_db_entry.delete(0, END)
        self.ps_ip.delete(0, END)
        self.ps_ip.insert(0, 'localhost:80')
        self.ps_ip.insert(END, '')

        for tr in [self.ps_login, self.ps_login_label, self.ps_password, self.ps_password_label]:
            tr.grid_remove()

    def mask(self):
        for to_f in [self.gdr_dsn, self.gdr_dsn_label, self.btn_resetdb]:
            to_f.grid_forget()
