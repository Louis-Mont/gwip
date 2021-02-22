from gw_logging.Log import Log
from datetime import datetime
from tkinter import Tk
from utils import dict_to_str, l_to_str, kcv, rev_col
from yesno import yesno
import pymysql
import pypyodbc


class Core:
    product_cols = ["IDProduit", "Commentaire", "Désignation", "Hauteur", "IDCatégorie", "IDsous_Catégorie", "Largeur",
                    "Nombre",
                    "NumTVA", "Poids", "PoidsUnitaire", "PourcPromo", "Prix_Etiquette", "PrixPromo", "PrixUnitaire",
                    "PrixUnitCollecte", "Profondeur", "stocRestant", "Volume", "VolumeUnitaire"]

    def __init__(self, log_interface, frame):
        """
        :type log_interface: Log
        :type frame: Tk
        """
        self.i_log = log_interface
        self.frame = frame

    def connect(self, dsn, ip, login, pwd, name):
        db_ps = None
        self.i_log.add("Connexion à la base de données prestashop")
        try:
            db_ps = pymysql.connect(host=ip, user=login,
                                    password=pwd, database=name)
            self.i_log.add("Connexion réussie")
        except pymysql.err.OperationalError as OEr:
            self.i_log.add(f"{OEr.args[1]}")

        self.i_log.add("Connexion à la BDD de gdr ")
        # debug = f"DSN={gdr_dsn.get()}"
        db_gdr = pypyodbc.connect(f"DSN={dsn}")
        self.i_log.add("Connexion réussie")
        return db_ps, db_gdr

    def del_cat(self, ps_db):
        cur_ps_db = ps_db.cursor()
        self.i_log.add("Suppression des catégories de prestashop")
        cur_ps_db.execute("DELETE FROM ps_category WHERE id_category NOT IN (1,2)")
        cur_ps_db.execute(
            "DELETE FROM ps_category_group WHERE id_category NOT IN (1,2)")
        cur_ps_db.execute(
            "DELETE FROM ps_category_lang WHERE id_category NOT IN (1,2)")
        cur_ps_db.execute("DELETE FROM ps_category_product")
        cur_ps_db.execute(
            "DELETE FROM ps_category_shop WHERE id_category NOT IN (1,2)")
        ps_db.commit()
        self.i_log.add("Catégories supprimées")

    def del_prod(self, ps_db):
        cur_ps_db = ps_db.cursor()
        self.i_log.add("Suppression des produits de prestashop")
        cur_ps_db.execute("DELETE FROM ps_product")
        cur_ps_db.execute("DELETE FROM ps_product_attribute")
        cur_ps_db.execute("DELETE FROM ps_product_attribute_combination")
        cur_ps_db.execute("DELETE FROM ps_product_attribute_image")
        cur_ps_db.execute("DELETE FROM ps_product_attribute_shop")
        cur_ps_db.execute("DELETE FROM ps_product_lang")
        cur_ps_db.execute("DELETE FROM ps_product_shop")
        cur_ps_db.execute("DELETE FROM ps_stock_available")
        ps_db.commit()
        self.i_log.add("Produits supprimés")

    def del_img(self, ps_db):
        cur_ps_db = ps_db.cursor()
        self.i_log.add("Suppression des images de prestashop")
        cur_ps_db.execute("DELETE FROM ps_image")
        cur_ps_db.execute("DELETE FROM ps_image_lang")
        cur_ps_db.execute("DELETE FROM ps_image_type")
        ps_db.commit()
        self.i_log.add("Images supprimées")

    def df(self, table, cur_ps, n_conditions=None):
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

    def reset_db(self, dbs):
        """
        Only resets categories, products, images in the prestashop database
        """
        """tables = ["ps_image", "ps_image_lang", "ps_image_type", "ps_image_shop", "ps_product", "ps_product_lang",
                  "ps_product_shop","ps_stock_available"]
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
        ps_db = dbs[0]
        self.del_cat(ps_db)
        self.del_img(ps_db)
        self.del_prod(ps_db)

    def add_cat(self, cat, db_ps):
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
        self.set_lang('ps_category_lang', lang_dict, ps_cur)

        category_dict = {
            'id_category': f"{cat_id}",
            'id_parent': f"{2}",
            'level_depth': f"{2}",
            'active': f"{1}",
            'date_add': f"'{date}'",
            'date_upd': f"'{date}'"
        }
        self.ii('ps_category', category_dict, ps_cur)

        self.ii('ps_category_group', {
            'id_category': f"{cat_id}", 'id_group': f"{1}"}, ps_cur)

        ps_cat_shop_dict = {
            'id_category': f"{cat_id}",
            'id_shop': f"{1}",
            'position': f"{0}"
        }
        self.ii('ps_category_shop', ps_cat_shop_dict, ps_cur)

        return cat_id

    def ii(self, table, vals, cur, conditions=None):
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

    def set_lang(self, table, vals, cur, conditions=None, lang=2):
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
            self.ii(f'{table}', vals, cur, u_cond)

    def db_add_id(self, db_ps, ps_con, gdr_prod, title):
        ps_cur = db_ps.cursor()
        ps_cur.execute(f"SELECT id_product FROM ps_product")
        prod_id = len(ps_cur.fetchall()) + 1
        self.db_ii_id(db_ps, ps_con, gdr_prod, prod_id, title)

    # WARNING ps_con is a tuple and work directly in strings?
    def db_ii_id(self, db_ps, ps_con, gdr_prod, id_product, title, update=False):
        ps_cur = db_ps.cursor()
        if update:
            conditions = {'id_product': id_product}
        else:
            conditions = None
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ps_prod_dict = {
            'id_product': f"{id_product}",
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
        self.ii('ps_product', ps_prod_dict, ps_cur, conditions)

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
        self.ii('ps_product_shop', ps_prod_shop_dict, ps_cur, conditions)

        ps_prod_lang_dict = {
            'id_product': f"{id_product}",
            'name': f"'{title}'"
        }
        if conditions is not None:
            conditions['id_shop'] = f"{1}"
        self.set_lang('ps_product_lang', ps_prod_lang_dict, ps_cur, conditions)

        if conditions is not None:
            conditions.pop('id_shop')

        ps_cur.execute("SELECT id_stock_available FROM ps_stock_available")
        ps_stock_id = len(ps_cur.fetchall()) + 1
        ps_stock_a_dict = {
            'id_stock_available': f"{ps_stock_id}",
            'id_product': f"{id_product}",
            'id_product_attribute': f"{0}",
            'id_shop': f"{1}",
            'id_shop_group': f"{0}",
            'quantity': f"{gdr_prod['Nombre']}"
        }
        self.ii('ps_stock_available', ps_stock_a_dict, ps_cur, conditions)

        # 1 pour Root, 2 pour Home
        for id_cat in [1, 2, ps_con]:
            ps_cat_prod_dict = {
                'id_category': f"{id_cat}",
                'id_product': f"{id_product}",
                'position': f"{1}"
            }
            if conditions is not None:
                conditions['id_category'] = f"{id_cat}"
            self.ii('ps_category_product', ps_cat_prod_dict, ps_cur, conditions)

        db_ps.commit()

        if update:
            action = "mis à jour"
        else:
            action = "ajouté"
        self.i_log.add(f"Produit {action}")
        self.i_log.add(f"Nom : {ps_prod_lang_dict['name']}")
        for k, v in gdr_prod.items():
            self.i_log.add(f"{k}:{v}")

    def add_id(self, id_product, cat_name, title, dbs):
        """
        Add the corresponding id from the gdr db to the prestashop db
        :param id_product: id added form the gdr db to the prestashop db
        :type id_product: int
        :param cat_name: The category the product will be placed
        :type cat_name: str
        :param title: The title the product will have
        :type title: str
        :param dbs: Prestashop db on 0, GDR on 1
        :type dbs: tuple
        """
        db_ps = dbs[0]
        ps_cur = dbs[0].cursor()
        gdr_cur = dbs[1].cursor()
        # Photos not included atm
        self.i_log.add(f"Ajout du produit {id_product}")
        gdr_cur.execute(
            f"SELECT {l_to_str(self.product_cols)} FROM Produit WHERE IDProduit={id_product}")
        gdr_con = gdr_cur.fetchone()
        # print(gdr_con)
        if gdr_con is not None:
            gdr_prod = {}
            for v in range(len(gdr_con)):
                gdr_prod[self.product_cols[v]] = gdr_con[v]
            # print(gdr_prod)
            ps_cur.execute(
                f"SELECT id_category,name FROM ps_category_lang WHERE name='{cat_name}'")
            ps_con = ps_cur.fetchall()
            if len(ps_con) == 0:
                # Ajout catégorie
                self.i_log.add(f"Ajout {cat_name}")
                ps_con = self.add_cat(cat_name, db_ps)
                db_ps.commit()
                self.i_log.add(f"Catégorie {cat_name} ajoutée")
            else:
                ps_con = ps_con[0][0]
                self.i_log.add(f"Catégorie déjà trouvée")

            # Ajout Produit
            ps_cur.execute(
                f"SELECT id_product FROM ps_product WHERE reference={gdr_prod['IDProduit']}")
            id_prod = ps_cur.fetchone()
            if id_prod is not None:
                self.i_log.add(
                    f"La référence {gdr_prod['IDProduit']} existe déjà dans la base de donnée")
                yesno(self.frame, "Duplicata",
                      "La référence existe déjà dans la base de donnée, voulez-vous la mettre à jour?",
                      lambda: self.db_ii_id(db_ps, ps_con, gdr_prod, id_prod[0], True))
            else:
                self.db_add_id(db_ps, ps_con, gdr_prod, title)
        else:
            self.i_log.add(f"ID {id_product} incorrecte")

    def syncventes(self, dbs):
        ventes_cols = ['IDProduit', 'Montant', 'IDLignes_Vente']
        nvc = rev_col(ventes_cols)
        db_ps = dbs[0]
        ps_cur = dbs[0].cursor()
        gdr_cur = dbs[1].cursor()
        self.i_log.add("Synchronisation des ventes")

        ps_cur.execute(f"SELECT reference FROM ps_product")
        for id_prod in ps_cur.fetchall():
            # print(id_prod)
            gdr_cur.execute(
                f"SELECT {l_to_str(ventes_cols)} FROM Lignes_Vente WHERE IDProduit={id_prod[0]}")
            sells = gdr_cur.fetchall()
            # print(sells)
            for s1 in sells:
                ex_sum = 0
                for s2 in sells:
                    if s1[nvc['IDProduit']] == s2[nvc['IDProduit']]:
                        ex_sum += s2[nvc['Montant']]
                if ex_sum >= 0:
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
                        self.ii("ps_product", ps_prod_dict, ps_cur, cond)

                        ps_prod_shop_dict = ps_prod_dict
                        ps_prod_shop_dict.pop('quantity')
                        self.ii("ps_product_shop", ps_prod_shop_dict, ps_cur, cond)

                        self.i_log.add(f"{id_prod[0]} mis à jour")

        db_ps.commit()
        self.i_log.add("Synchronisation terminée")
