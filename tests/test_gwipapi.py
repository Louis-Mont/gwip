from tkinter import Tk, Text
from unittest import TestCase

from Api.Api import Api
from Api.DebugApi import DebugApi
from gw_logging.Log import Log
from prestapyt import PrestaShopWebServiceDict


class TestApi(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestApi, self).__init__(*args, **kwargs)
        self.frame = Tk()
        self.text_log = Text(self.frame)
        self.dsn = 'gdr'
        self.ip = 'http://localhost:80/prestashop'
        self.key = 'DKG6MFPXV7EHY83JQL5RSL7PZYDWKL21'
        self.api = Api(self.frame, Log(self.text_log), self.dsn, self.ip, self.key, DebugApi(True, True))

    def test_add_product(self):
        self.api.add_id(281474976713888, 'testestapi', 'Meubles')

    def test_delete(self):
        self.api.reset_db()
        self.assertEqual(len(self.api.get_indexes(('product', 'products'))), 0)
        self.assertEqual(len(self.api.get_indexes(('category', 'categories'))), 2)

    def test_sync_ventes(self):
        self.api.add_id(281474976714478, 'testsyncapi', 'Meubles')
        prods = self.api.api.get('products')['products']
        if prods != '':
            prods = prods['product']
            if not isinstance(prods, dict):
                prod = [int(attr['attrs']['id']) for attr in prods]
            else:
                prod = [int(prods['attrs']['id'])]
        else:
            self.fail()
        # debug = self.api.api.get('products', prod[-1])
        self.assertEqual(self.api.api.get('products', prod[-1])['product']['active'], '1')
        self.api.sync_ventes()
        self.assertEqual(self.api.api.get('products', prod[-1])['product']['active'], '0')

    def test_add_img(self):
        self.api.add_id(3, 'testimgapi', 'Vaisselle')
