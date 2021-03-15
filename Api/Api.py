from datetime import datetime
from tkinter import Tk

# The import is mistaking Api.py with the Api file
from Api.DebugApi import DebugApi
from gw_logging.Log import Log
from Core.Core import Core
from db_interface.DatabaseODBC import DatabaseODBC
from prestapyt import PrestaShopWebServiceDict
from utils import l_to_str, rev_col
from yesno import yesno


class Api(Core):
    def __init__(self, frame, log_interface, dsn, ip, key, debug=DebugApi()):
        """
        :type frame: Tk
        :type log_interface: Log
        :type dsn: str
        :type ip: str
        :type key: str
        """
        super().__init__(frame, log_interface)
        self.dsn = dsn
        self.ip = ip
        self.key = key
        self.debug = debug

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

    def add_id(self, id_product, title, cat_name, force=False):
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
            if self.requirements(reqs) or self.debug.force_reqs:
                prod_exists = False
                for id_prod in self.get_indexes(('product', 'products')):
                    if self.api.get('products', id_prod)['product']['reference'] == str(id_product):
                        prod_exists = True
                        break  # opti
                if prod_exists and not self.debug.force_yes:
                    self.i_log.add(f"La référence {id_product} existe déjà dans la base de données")
                    yesno(self.frame, "Duplicata",
                          "La référence existe déjà dans la base de données, voulez-vous la mettre à jour?",
                          lambda: self.do_prod(id_product, title, cat_name, gdr_prod, True))
                else:
                    self.do_prod(id_product, title, cat_name, gdr_prod, prod_exists)
        else:
            self.i_log.add(f"ID {id_product} incorrecte")
        return False

    def do_prod(self, id_product, title, cat_name, gdr_prod, edit=False):
        """
        :param id_product: The IDProduit in GDR
        :type id_product: int
        :type title: str
        :type cat_name: str
        :param gdr_prod: {title : field} of the Produit table in HDR
        :type gdr_prod: dict
        :param edit: if the object is edited or simply added
        :return: The JSON response when the product was added
        :rtype: dict
        """
        # Ajout ou non de catégorie
        cat_exists = self.x_exists(('category', 'categories'), 'name', cat_name)
        id_cat = cat_exists[1]
        if cat_exists[0]:
            self.i_log.add("Catégorie trouvée")
        else:
            self.i_log.add(f"Ajout {cat_name}")
            id_cat = self.add_cat(cat_name)['id']

        # Ajout produit
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prod_schema = self.api.get('products', options={'schema': 'blank'})['product']
        prod_dict = {
            'id_category_default': f"{id_cat}",
            'id_shop_default': f"{1}",
            'reference': f"{id_product}",
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
            'condition': f"refurbished",
            'date_add': f"{date}",
            'date_upd': f"{date}"
        }
        if float(prod_dict['price']) == 0:
            self.i_log.add("Le prix de ce produit était à 0, il a été mis à 1")
            prod_dict['price'] = '1.0'
        prod_schema = {**prod_schema, **prod_dict}
        link_rewrite = cat_name.lower().encode("ascii", "ignore").decode("utf-8")
        self.set_lang(prod_schema, 'link_rewrite', link_rewrite)
        self.set_lang(prod_schema, 'name', title)
        # Association des catégories au produit
        prod_schema['associations']['categories']['category'] = [{'id': '2'}, {'id': f"{id_cat}"}]
        # Edit de l'objet si exigé
        if edit:
            p_idx = self.get_indexes(('product', 'products'))
            i = len(p_idx)
            for i in p_idx:
                currprod = self.api.get('products', i)['product']
                if currprod['reference'] == str(id_product):
                    break
            prod_schema['id'] = i
            p_act = self.api.edit
        else:
            p_act = self.api.add
        last_prod = p_act('products', {'product': prod_schema})['prestashop']['product']

        # Ajout quantité
        sa_schema = self.api.get('stock_availables', options={'schema': 'blank'})['stock_available']
        prod_asc = last_prod['associations']
        sa_dict = {
            'id': f"{prod_asc['stock_availables']['stock_available']['id']}",
            'id_product': f"{last_prod['id']}",
            'id_product_attribute': f"{prod_asc['stock_availables']['stock_available']['id_product_attribute']}",
            'id_shop': f"{1}",
            'quantity': f"{gdr_prod['Nombre']}",
            'depends_on_stock': f"{0}",
            'out_of_stock': f"{2}"
        }
        sa_schema = {**sa_schema, **sa_dict}
        self.api.edit('stock_availables', {'stock_available': sa_schema})

    def add_cat(self, cat):
        """
        :param cat: The name of the category to add
        :type cat: str
        :return: The JSON response when the category was added
        """
        cat_schema = self.api.get('categories', options={'schema': 'blank'})['category']
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cat_dict = {
            'id_parent': f"{2}",
            'active': f"{1}",
            'position': f"{0}",
            'date_add': f"{date}",
            'date_upd': f"{date}",
        }
        # https://stackoverflow.com/questions/38987/how-do-i-merge-two-dictionaries-in-a-single-expression-taking-union-of-dictiona/228366#228366
        cat_schema = {**cat_schema, **cat_dict}
        self.set_lang(cat_schema, 'name', cat)
        link_rewrite = cat.lower().encode("ascii", "ignore").decode("utf-8")
        self.set_lang(cat_schema, 'link_rewrite', link_rewrite)
        return self.api.add('categories', {'category': cat_schema})['prestashop']['category']

    def sync_ventes(self):
        self._connect()
        gdr_cur = self.gdr_db.DB.cursor()
        self.i_log.add("Synchronisation des ventes")
        for id_prod in self.get_indexes(('product', 'products')):
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
                    if self.x_exists(('product', 'products'), 'reference', reference)[0]:
                        # Modification produit
                        prod_schema = self.api.get('products', id_prod)['product']
                        prod = {
                            'on_sale': f"{0}",
                            'active': f"{0}",
                            'available_for_order': f"{0}"
                        }
                        # TODO modify quantity in stock_available
                        prod_schema = {**prod_schema, **prod}
                        prod_schema.pop('manufacturer_name')
                        prod_schema.pop('quantity')
                        # The position in category is sometimes over evaluated
                        pos_cat = int(prod_schema['position_in_category']['value'])
                        if pos_cat > 0:
                            pos_cat -= 1
                        prod_schema['position_in_category']['value'] = f"{pos_cat}"
                        last_prod = self.api.edit('products', {'product': prod_schema})['prestashop']['product']

                        # Modification quantité
                        sa_schema = self.api.get('stock_availables', int(
                            last_prod['associations']['stock_availables']['stock_available']['id']))[
                            'stock_available']
                        sa = {
                            'quantity': f"{0}",
                            'out_of_stock': f"{1}"
                        }
                        sa_schema = {**sa_schema, **sa}
                        self.api.edit('stock_availables', {'stock_available': sa_schema})
                        self.i_log.add(f"{id_prod} mis à jour")

    def set_lang(self, schema, key, name):
        # e.g. key : {'language': [{'attrs': {'id': '1'}, 'value': name}, {'attrs': {'id': '2'}, 'value': name}]}
        try:
            for langs in schema[key]['language']:
                langs['value'] = name
            return schema
        except KeyError:
            schema[key] = {'language': [{'attrs': {'id': '1'}, 'value': ''}, {'attrs': {'id': '2'}, 'value': ''}]}
            return self.set_lang(schema, key, name)

    def reset_db(self):
        self._connect()
        prods = self.get_indexes(('product', 'products'))
        if prods:
            self.i_log.add("Suppression des produits")
            self.api.delete('products', prods)
            self.i_log.add("Produits supprimés")
        cats = self.get_indexes(('category', 'categories'))[2:]
        if cats:
            self.i_log.add("Suppression des catégories")
            self.api.delete('categories', cats)
            self.i_log.add("Catégories supprimées")
        # stock_available n'est pas deletable

    def x_exists(self, head_name, x, name):
        """
        Check if the name exists in the objects list
        :param head_name: singular[0], plural[1]
        :type head_name: tuple
        :param x: The column you're looking into
        :type x: str
        :type name: str
        :return: [0] : exists?, [1]: where in the list
        :rtype: tuple
        """
        id = 0
        for id in self.get_indexes(head_name):
            col = self.api.get(head_name[1], id)[head_name[0]][x]
            if isinstance(col, dict):
                if col['language'][0]['value'] == name:
                    return True, id
            if col == name:
                return True, id
        return False, id

    def get_indexes(self, head_name):
        """
        Get all indexes for the head_name
        :param head_name: singular[0], plural[1]
        :type head_name: tuple
        :rtype: list
        """
        head = self.api.get(head_name[1])[head_name[1]]
        if head != '':
            hh = head[head_name[0]]
            if not isinstance(hh, dict):
                return [int(attr['attrs']['id']) for attr in hh]
            return [int(hh['attrs']['id'])]
        return []
