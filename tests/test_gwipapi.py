from tkinter import Tk, Text
from unittest import TestCase

from Api.Api import Api
from gw_logging.Log import Log
from prestapyt import PrestaShopWebServiceDict


class TestApi(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestApi, self).__init__(*args, **kwargs)
        self.frame = Tk()
        self.text_log = Text(self.frame)
        self.dsn = 'gdr'
        self.ip = 'http://localhost:80/prestashop'
        self.key = 'KKLSZNHGZI21FJQE3ZVR55F1JPLRW7VZ'
        self.api = Api(self.frame, Log(self.text_log), self.dsn, self.ip, self.key)

    def test_add_product(self):
        ps = PrestaShopWebServiceDict(self.ip, self.key)
        old_qt = len([int(attr['attrs']['id']) for attr in ps.get('products')['products']['product']])
        # debug = ps.get('products', 1)
        self.api.add_id(281474976713888, 'testestapi', 'Meubles')
        new_qt = len(self.api.get_indexes(('product', 'products')))
        self.assertEqual(old_qt + 1, new_qt)
