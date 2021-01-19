import pymysql
import pypyodbc
from tkinter import END, Tk, Entry, StringVar, Label, RAISED, Button, OptionMenu, Text, Scrollbar
from datetime import datetime
from utils import dict_to_str, l_to_str, kcv, rev_col
from yesno import yesno

VERSION = '1.3.0 EXPERIMENTAL'

cats = ['Meubles', 'Electroménagers', 'Multimédias', 'Textile', 'Culture', 'Loisirs', 'Vaisselle',
        'Bricolage-Jardinage',
        'Décoration-Bibelot', 'Puériculture']

PS_DB: pymysql.Connection = None
GDR_DB: pypyodbc.Connection = None


def log_add(lg: str):
    # print(lg)
    log.configure(state="normal")
    log.insert(END, f"\n{lg}")
    log.configure(state="disabled")


def del_cat(ps_db: pypyodbc.Connection):
    cur_ps_db = ps_db.cursor()
    log_add("Suppression des catégories de prestashop")
    cur_ps_db.execute("DELETE FROM ps_category WHERE id_category NOT IN (1,2)")
    cur_ps_db.execute(
        "DELETE FROM ps_category_group WHERE id_category NOT IN (1,2)")
    cur_ps_db.execute(
        "DELETE FROM ps_category_lang WHERE id_category NOT IN (1,2)")
    cur_ps_db.execute("DELETE FROM ps_category_product")
    cur_ps_db.execute(
        "DELETE FROM ps_category_shop WHERE id_category NOT IN (1,2)")
    ps_db.commit()
    log_add("Catégories supprimées")


def del_prod(ps_db: pypyodbc.Connection):
    cur_ps_db = ps_db.cursor()
    log_add("Suppression des produits de prestashop")
    cur_ps_db.execute("DELETE FROM ps_product")
    cur_ps_db.execute("DELETE FROM ps_product_attribute")
    cur_ps_db.execute("DELETE FROM ps_product_attribute_combination")
    cur_ps_db.execute("DELETE FROM ps_product_attribute_image")
    cur_ps_db.execute("DELETE FROM ps_product_attribute_shop")
    cur_ps_db.execute("DELETE FROM ps_product_lang")
    cur_ps_db.execute("DELETE FROM ps_product_shop")
    cur_ps_db.execute("DELETE FROM ps_stock_available")
    ps_db.commit()
    log_add("Produits supprimés")


def del_img(ps_db: pypyodbc.Connection):
    cur_ps_db = ps_db.cursor()
    log_add("Suppression des images de prestashop")
    cur_ps_db.execute("DELETE FROM ps_image")
    cur_ps_db.execute("DELETE FROM ps_image_lang")
    cur_ps_db.execute("DELETE FROM ps_image_type")
    ps_db.commit()
    log_add("Images supprimées")


def df(table: str, cur_ps: pypyodbc.Cursor, n_conditions: tuple = None):
    """
    Delete all content from the table not in conditions
    :param table: The table you're deleting from
    :param cur_ps: The cursor of the DB
    :param n_conditions: The no conditions
    """
    if n_conditions is None:
        cur_ps.execute(f"DELETE FROM {table}")
    else:
        cur_ps.execute(f"DELETE FROM {table} WHERE {n_conditions[0]} NOT IN ({l_to_str(n_conditions[1])})")


def reset_db():
    """
    Only resets categories, products, images in the prestashop database
    """
    """tables = ["ps_image", "ps_image_lang", "ps_image_type", "ps_image_shop", "ps_product", "ps_product_lang",
              "ps_product_shop"]
    tables_cat = ["ps_category", "ps_category_group", "ps_category_lang", "ps_category_shop"]
    n_c = ('id_category', (1, 2))
    PS_DB, GDR_DB = main()
    ps_db = PS_DB
    cur_ps = ps_db.cursor()
    for t in tables:
        df(t, cur_ps)
    for t in tables_cat:
        df(t, cur_ps, n_c)
    ps_db.commit()"""
    PS_DB, GDR_DB = main()
    ps_db = PS_DB
    del_cat(ps_db)
    del_img(ps_db)
    del_prod(ps_db)


def add_cat(cat: str, db_ps: pypyodbc.Connection) -> int:
    """
    Add category cat into prestashop's db_ps
    :param cat: The name of the category added
    :param db_ps: The prestashop db
    :return: The id of the category added
    """
    ps_cur = db_ps.cursor()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ps_cur.execute(f"SELECT id_category FROM ps_category")
    cat_id = len(ps_cur.fetchall()) + 1
    lang_dict = {
        'id_category': f"{cat_id}",
        'name': f"'{cat}'",
    }
    set_lang('ps_category_lang', lang_dict, ps_cur)

    category_dict = {
        'id_category': f"{cat_id}",
        'id_parent': f"{2}",
        'level_depth': f"{2}",
        'active': f"{1}",
        'date_add': f"'{date}'",
        'date_upd': f"'{date}'"
    }
    ii('ps_category', category_dict, ps_cur)

    ii('ps_category_group', {
        'id_category': f"{cat_id}", 'id_group': f"{1}"}, ps_cur)

    ps_cat_shop_dict = {
        'id_category': f"{cat_id}",
        'id_shop': f"{1}",
        'position': f"{0}"
    }
    ii('ps_category_shop', ps_cat_shop_dict, ps_cur)

    return cat_id


def ii(table: str, vals: dict, cur: pypyodbc.Cursor, conditions: dict = None):
    """
    Inserts into the table vals using cur
    :param table: The table you're inserting into
    :param vals: The keys represent the titles and values the values inserted into said columns
    :param cur: The cursor used to communicate with the db
    :param conditions: The names of the columns you're checking in n,0 and their values in n,1
    """
    if conditions is None:
        keys, values = dict_to_str(vals)
        cur.execute(
            f"INSERT INTO {table} ({keys}) VALUES ({values})")
    else:
        # Update
        u_vals = vals.copy()
        for c in conditions:
            try:
                u_vals.pop(c)
            except KeyError:
                pass
        # debug = f"UPDATE {table} SET {kcv(u_vals, '=')} WHERE {kcv(conditions, '=', ' AND ')}"
        cur.execute(
            f"UPDATE {table} SET {kcv(u_vals, '=')} WHERE {kcv(conditions, '=', ' AND ')}")


def set_lang(table: str, vals: dict, cur: pypyodbc.Cursor, conditions: dict = None, lang: int = 2):
    """
    Sets the different name the item can have following the different languages you can have
    :param table: table where the different languages are stocked
    :param vals: all the fields to change without `lang` and `link_rewrite` columns
    :param cur: Cursor of the db you're executing on
    :param conditions: if there is an update, the name of the column in 0 and the value in 1
    :param lang: By default 2, english(1) and french(2)
    """
    for lang in range(1, lang + 1):
        link_rewrite = vals['name'].lower().encode(
            "ascii", "ignore").decode("utf-8")
        vals['link_rewrite'] = f"{link_rewrite}"
        vals['id_lang'] = f"{lang}"
        u_cond = None
        if conditions is not None:
            u_cond = conditions.copy()
            u_cond['id_lang'] = vals['id_lang']
        ii(f'{table}', vals, cur, u_cond)


def db_add_id(db_ps: pymysql.Connection, ps_con: tuple, gdr_prod: dict):
    ps_cur = db_ps.cursor()
    ps_cur.execute(f"SELECT id_product FROM ps_product")
    prod_id = len(ps_cur.fetchall()) + 1
    db_ii_id(db_ps, ps_con, gdr_prod, prod_id)


# WARNING ps_con is a tuple and work directly in strings?
def db_ii_id(db_ps: pymysql.Connection, ps_con: tuple, gdr_prod: dict, id: int, update: bool = False):
    ps_cur = db_ps.cursor()
    if update:
        conditions = {'id_product': id}
    else:
        conditions = None
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ps_prod_dict = {
        'id_product': f"{id}",
        'id_category_default': f"{ps_con}",
        'id_tax_rules_group': f"{0}",
        'on_sale': f"{1}",
        'quantity': f"{gdr_prod['Nombre']}",
        'price': f"{gdr_prod['PrixUnitaire']}",
        'wholesale_price': f"{int(gdr_prod['PrixUnitaire']) * int(gdr_prod['Nombre'])}",
        'reference': f"'{gdr_prod['IDProduit']}'",
        'width': f"{gdr_prod['Largeur']}",
        'height': f"{gdr_prod['Hauteur']}",
        'depth': f"{gdr_prod['Profondeur']}",
        'weight': f"{gdr_prod['Poids']}",
        'redirect_type': f"'301-product'",
        'date_add': f"'{date}'",
        'date_upd': f"'{date}'"
    }
    ii('ps_product', ps_prod_dict, ps_cur, conditions)

    # The ps_product_shop db is almost similar the the ps_product one
    ps_prod_shop_dict = ps_prod_dict.copy()
    ps_prod_shop_dict['active'] = f"{1}"
    ps_prod_shop_dict['id_shop'] = f"{1}"
    ps_prod_shop_dict.pop('width')
    ps_prod_shop_dict.pop('height')
    ps_prod_shop_dict.pop('depth')
    ps_prod_shop_dict.pop('quantity')
    ps_prod_shop_dict.pop('reference')
    ps_prod_shop_dict.pop('weight')
    ii('ps_product_shop', ps_prod_shop_dict, ps_cur, conditions)

    ps_prod_lang_dict = {
        'id_product': f"{id}",
        'name': f"'{ps_title.get()}'"
    }
    if conditions is not None:
        conditions['id_shop'] = f"{1}"
    set_lang('ps_product_lang', ps_prod_lang_dict, ps_cur, conditions)

    if conditions is not None:
        conditions.pop('id_shop')

    ps_cur.execute("SELECT id_stock_available FROM ps_stock_available")
    ps_stock_id = len(ps_cur.fetchall()) + 1
    ps_stock_a_dict = {
        'id_stock_available': f"{ps_stock_id}",
        'id_product': f"{id}",
        'id_product_attribute': f"{0}",
        'id_shop': f"{1}",
        'id_shop_group': f"{0}",
        'quantity': f"{gdr_prod['Nombre']}"
    }
    ii('ps_stock_available', ps_stock_a_dict, ps_cur, conditions)

    # 1 pour Root, 2 pour Home
    for id_cat in [1, 2, ps_con]:
        ps_cat_prod_dict = {
            'id_category': f"{id_cat}",
            'id_product': f"{id}",
            'position': f"{1}"
        }
        if conditions is not None:
            conditions['id_category'] = f"{id_cat}"
        ii('ps_category_product', ps_cat_prod_dict, ps_cur, conditions)

    db_ps.commit()

    if update:
        action = "mis à jour"
    else:
        action = "ajouté"
    log_add(f"Produit {action}")
    log_add(f"Nom : {ps_prod_lang_dict['name']}")
    for k, v in gdr_prod.items():
        log_add(f"{k}:{v}")


product_cols = ["IDProduit", "Commentaire", "Désignation", "Hauteur", "IDCatégorie", "IDsous_Catégorie", "Largeur",
                "Nombre",
                "NumTVA", "Poids", "PoidsUnitaire", "PourcPromo", "Prix_Etiquette", "PrixPromo", "PrixUnitaire",
                "PrixUnitCollecte", "Profondeur", "stocRestant", "Volume", "VolumeUnitaire"]


def add_id(id: int):
    """
    Add the corresponding id from the gdr db to the prestashop db
    :param id: id added form the gdr db to the prestashop db
    """
    PS_DB, GDR_DB = main()
    db_ps, db_gdr = PS_DB, GDR_DB
    ps_cur = db_ps.cursor()
    gdr_cur = db_gdr.cursor()
    # Photos not included atm
    log_add(f"Ajout du produit {id}")
    gdr_cur.execute(
        f"SELECT {l_to_str(product_cols)} FROM Produit WHERE IDProduit={id}")
    gdr_con = gdr_cur.fetchone()
    # print(gdr_con)
    if gdr_con is not None:
        gdr_prod = {}
        for v in range(len(gdr_con)):
            gdr_prod[product_cols[v]] = gdr_con[v]
        # print(gdr_prod)
        ps_cur.execute(
            f"SELECT id_category,name FROM ps_category_lang WHERE name='{ps_cat_def.get()}'")
        ps_con = ps_cur.fetchall()
        if len(ps_con) == 0:
            # Ajout catégorie
            log_add(f"Ajout {ps_cat_def.get()}")
            ps_con = add_cat(ps_cat_def.get(), db_ps)
            db_ps.commit()
            log_add(f"Catégorie {ps_cat_def.get()} ajoutée")
        else:
            ps_con = ps_con[0][0]
            log_add(f"Catégorie déjà trouvée")

        # Ajout Produit
        ps_cur.execute(
            f"SELECT id_product FROM ps_product WHERE reference={gdr_prod['IDProduit']}")
        id_prod = ps_cur.fetchone()
        if id_prod is not None:
            log_add(
                f"La référence {gdr_prod['IDProduit']} existe déjà dans la base de donnée")
            yesno(frame, "Duplicata",
                  "La référence existe déjà dans la base de donnée, voulez-vous la mettre à jour?",
                  lambda: db_ii_id(db_ps, ps_con, gdr_prod, id_prod[0], True))
        else:
            db_add_id(db_ps, ps_con, gdr_prod)
    else:
        log_add(f"ID {id} incorrecte")


def syncventes():
    ventes_cols = ['IDProduit', 'Montant', 'IDLignes_Vente']
    nvc = rev_col(ventes_cols)
    PS_DB, GDR_DB = main()
    db_ps, db_gdr = PS_DB, GDR_DB
    ps_cur = db_ps.cursor()
    gdr_cur = db_gdr.cursor()
    log_add("Synchronisation des ventes")

    ps_cur.execute(f"SELECT reference FROM ps_product")
    for id_prod in ps_cur.fetchall():
        # print(id_prod)
        gdr_cur.execute(
            f"SELECT {l_to_str(ventes_cols)} FROM Lignes_Vente WHERE IDProduit={id_prod[0]}")
        sells = gdr_cur.fetchall()
        # print(sells)
        for s1 in sells:
            sum = 0
            for s2 in sells:
                if s1[nvc['IDProduit']] == s2[nvc['IDProduit']]:
                    sum += s2[nvc['Montant']]
            if sum >= 0:
                ps_cur.execute(
                    f"SELECT id_product FROM ps_product WHERE reference='{id_prod[0]}'")
                ps_con = ps_cur.fetchone()
                # print(ps_con[0])
                # print(id_prod[0])
                if ps_con is not None:
                    cond = {'id_product': ps_con[0]}
                    ps_prod_dict = {
                        'on_sale': f"{0}",
                        'quantity': f"{0}",
                        'active': f"{0}",
                        'available_for_order': f"{0}"
                    }
                    ii("ps_product", ps_prod_dict, ps_cur, cond)

                    ps_prod_shop_dict = ps_prod_dict
                    ps_prod_shop_dict.pop('quantity')
                    ii("ps_product_shop", ps_prod_shop_dict, ps_cur, cond)

                    log_add(f"{id_prod[0]} mis à jour")

    db_ps.commit()
    log_add("Synchronisation terminée")


def main():
    prestashop_ip = ps_ip.get()
    prestashop_login = ps_login.get()
    prestashop_pwd = ps_password.get()
    prestashop_db_name = ps_db_entry.get()

    db_ps = None
    log_add("Connexion à la base de données prestashop")
    try:
        db_ps = pymysql.connect(host=prestashop_ip, user=prestashop_login,
                                password=prestashop_pwd, database=prestashop_db_name)
        log_add("Connexion réussie")
    except pymysql.err.OperationalError as OEr:
        log_add(f"{OEr.args[1]}")

    log_add("Connexion à la BDD de gdr ")
    # debug = f"DSN={gdr_dsn.get()}"
    db_gdr = pypyodbc.connect(f"DSN={gdr_dsn.get()}")
    log_add("Connexion réussie")

    """cur_ps = db_ps.cursor()
    cur_db = db_gdr.cursor()

    cur_ps.execute("SHOW TABLES")
    tables = cur_ps.fetchall()
    print(tables)
    i = 0
    for table in tables:
        # tables[0]
        cur_ps.execute(f"SELECT * FROM {table[0]}")
        for results in cur_ps.fetchall():
            for fields in results:
                try:
                    if int(fields) == 300:
                        print(f"{tables[i][0]}\t{fields}")
                except ValueError:
                    pass
                except TypeError:
                    pass
        i += 1"""

    return db_ps, db_gdr


def on_closing(dbs: list, names: list):
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
    ps_cat_text.set("Categorie prestashop")
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

    ps_title = Entry(frame)
    ps_title.insert(0, '')
    ps_title.insert(END, '')
    ps_title.grid(row=4, column=1)

    log = Text(frame, wrap='word')
    log.insert(END, 'Logs :')
    log.configure(state='disabled')
    log.grid(row=5, column=0, columnspan=4)

    log_scroll = Scrollbar(frame, command=log.yview)
    log_scroll.grid(row=5, column=3, sticky='nse')
    log['yscrollcommand'] = log_scroll.set

    btn_addid = Button(frame, text='Add',
                       command=lambda: add_id(int(gdr_id.get())))
    btn_addid.grid(row=3, column=2)

    btn_resetdb = Button(frame, text='Reset DB', command=lambda: reset_db())
    btn_resetdb.grid(row=3, column=3)

    btn_syncventes = Button(
        frame, text='Synchroniser Ventes', command=lambda: syncventes())
    btn_syncventes.grid(row=4, column=2)

    # btn_resetdb.grid_remove()
    frame.protocol("WM_DELETE_WINDOW", lambda: on_closing(
        [PS_DB, GDR_DB], ['Prestashop', 'GDR']))
    frame.mainloop()

    input()
