from datetime import datetime

from Core.Core import Core
from db_interface.DatabaseODBC import DatabaseODBC
from prestapyt import PrestaShopWebServiceDict

from utils import l_to_str, rev_col
from yesno import yesno


class Api(Core):
    def __init__(self, frame, log_interface, dsn, ip, key):
        super().__init__(frame, log_interface)
        self.dsn = dsn
        self.ip = ip
        self.key = key

    def _connect(self):
        """
        Connects to the API and the GDR DB
        """
        self.i_log.add("Connection à la BDD GDR")
        self.gdr_db = DatabaseODBC()
        if self.gdr_db.connect(self.dsn):
            self.i_log.add("Connexion réussie")
        else:
            self.i_log.add("Connexion échouée")
        #
        self.i_log.add("Connection à l'API")
        self.api = PrestaShopWebServiceDict(self.ip, self.key)
        self.i_log.add("Connection réussie")

    def add_id(self, id_product, title, cat_name):
        self._connect()
        gdr_cur = self.gdr_db.DB.cursor()
        # Photos not included atm
        self.i_log.add(f"Ajout du produit {id_product}")
        gdr_cur.execute(f"SELECT {l_to_str(self.product_cols)} FROM Produit WHERE IDProduit={id_product}")
        gdr_con = gdr_cur.fetchone()
        if gdr_con is not None:
            gdr_prod = {}
            for v in range(len(gdr_con)):
                gdr_prod[self.product_cols[v]] = gdr_con[v]
            reqs = [
                (gdr_prod['Nombre'], ([0], False, "La quantité de ce produit est à 0")),
                (gdr_prod['IDSortie'], ([0, 1], True, "Ce produit ne peut pas être mis en vente"))
            ]
            if self.requirements(reqs):
                # Ajout ou non de catégorie
                cat_exists = False
                id_cat = 0
                for id_cat in self.get_indexes(self.api.get('categories')['categories']['category']):
                    # debug = self.api.get('categories', id_cat)
                    if self.api.get('categories', id_cat)['category']['name']['language'][0]['attrs'] == cat_name:
                        cat_exists = True
                        break
                if cat_exists:
                    self.i_log.add("Catégorie trouvée")
                else:
                    self.i_log.add(f"Ajout {cat_name}")
                    self.add_cat(cat_name)
                    id_cat += 1

                # Ajout produit
                date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                prod_schema = self.api.get('products', options={'schema': 'blank'})['product']
                prod_dict = {
                    'id_category_default': f"{id_cat}",
                    'id_shop_default': f"{1}",
                    'reference': f"{id_product}",
                    'quantity': f"{gdr_prod['Nombre']}",
                    'width': f"{gdr_prod['Largeur']}",
                    'height': f"{gdr_prod['Hauteur']}",
                    'depth': f"{gdr_prod['Profondeur']}",
                    'weight': f"{gdr_prod['Poids']}",
                    'state': f"{1}",
                    'minimal_quantity': f"{1}",
                    'price': f"{float(gdr_prod['PrixUnitaire'])}",
                    'wholesale_price': f"{int(gdr_prod['PrixUnitaire']) * int(gdr_prod['Nombre'])}",
                    'active': f"{1}",
                    'redirect_type': f"'301-product'",
                    'available_for_order': f"{1}",
                    'show_condition': f"{1}",
                    'show_price': f"{1}",
                    'condition': f"'refurbished'",
                    'date_add': f"'{date}'",
                    'date_upd': f"'{date}'"
                }
                if float(prod_dict['price']) < 1:
                    self.i_log.add("Le prix de ce produit était à 0, il a été mis à 1")
                    prod_dict['price'] = 1.0
                prod_schema = {**prod_schema, **prod_dict}
                link_rewrite = cat_name.lower().encode("ascii", "ignore").decode("utf-8")
                self.set_lang(prod_schema, 'link_rewrite', link_rewrite)
                self.set_lang(prod_schema, 'name', title)

                prod_exists = False
                id_prod = 0
                for id_prod in self.get_indexes(self.api.get('products')['products']['product']):
                    if self.api.get('products', id_prod)['product']['reference'] == id_product:
                        prod_exists = True
                if prod_exists:
                    prod_schema['id'] = f"{id_prod}"
                    self.i_log.add(f"La référence {id_product} existe déjà dans la base de données")
                    yesno(self.frame, "Duplicata",
                          "La référence existe déjà dans la base de données, voulez-vous la mettre à jour?",
                          lambda: self.api.edit('products', prod_schema))
                else:
                    self.api.add('products', prod_schema)
        else:
            self.i_log.add(f"ID {id_product} incorrecte")

    def add_cat(self, cat_name):
        cat_schema = self.api.get('categories', options={'schema': 'blank'})['category']
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cat_dict = {
            'id_parent': f"{2}",
            'active': f"{1}",
            'position': f"{0}",
            'date_add': f"'{date}'",
            'date_upd': f"'{date}'",
        }
        # https://stackoverflow.com/questions/38987/how-do-i-merge-two-dictionaries-in-a-single-expression-taking-union-of-dictiona/228366#228366
        cat_schema = {**cat_schema, **cat_dict}
        self.set_lang(cat_schema, 'name', cat_name)
        link_rewrite = cat_name.lower().encode("ascii", "ignore").decode("utf-8")
        self.set_lang(cat_schema, 'link_rewrite', link_rewrite)

    def sync_ventes(self):
        self._connect()
        gdr_cur = self.gdr_db.DB.cursor()
        self.i_log.add("Synchronisation des ventes")
        for id_prod in self.get_indexes(self.api.get('products')['products']['product']):
            nvc = rev_col(self.ventes_cols)
            reference = self.api.get('products', id_prod)['product']['reference']
            gdr_cur.execute(
                f"SELECT {l_to_str(self.ventes_cols)} FROM Lignes_Vente WHERE IDProduit={reference}")
            sells = gdr_cur.fetchall()
            for s1 in sells:
                ex_sum = 0
                for s2 in sells:
                    if s1[nvc['IDProduit']] == s2[nvc['IDProduit']]:
                        ex_sum += s2[nvc['Montant']]
                if ex_sum >= 0:
                    if self.x_exists(('product', 'products'), 'reference', str(id_prod)):
                        prod_schema = self.api.get('products', options={'schema': 'blank'})['product']
                        prod = {
                            'on_sale': f"{0}",
                            'quantity': f"{0}",
                            'active': f"{0}",
                            'available_for_order': f"{0}"
                        }
                        prod_schema = {**prod_schema, **prod}
                        self.api.edit('product', id_prod, prod_schema)
                        self.i_log.add(f"{id_prod[0]} mis à jour")

    def set_lang(self, schema, key, name):
        # e.g. : name : {'language': [{'attrs': {'id': '1'}, 'value': ''}, {'attrs': {'id': '2'}, 'value': ''}]}
        for langs in schema[key]['language']:
            langs['value'] = name
        return schema

    def reset_db(self):
        self.api.delete('product', self.get_indexes(self.api.get('products')['products']['product']))
        self.api.delete('categories', self.get_indexes(self.api.get('categories')['categories']['category']))

    def x_exists(self, head_name, x, name):
        """
        Check if the name exists in the objects list
        :param head_name: singular[0], plural[1]
        :type head_name: tuple
        :param x: The column you're looking into
        :type x: str
        :type name: str
        :rtype: bool
        """
        for id_cat in self.get_indexes(self.api.get(head_name[1])[head_name[1]][head_name[0]]):
            if self.api.get(head_name[1], id_cat)[x]['language'][0]['value'] == name:
                return True
        return False

    def get_indexes(self, obj_list):
        return [int(attr['attrs']['id']) for attr in obj_list]
