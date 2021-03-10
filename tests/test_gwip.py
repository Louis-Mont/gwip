from unittest import TestCase
from Core.Core import Core
from gw_logging.Log import Log
from tkinter import Text, Tk
from db_interface.DatabaseMySQL import DatabaseMySLQ


class Test(TestCase):
    def __init__(self, *args, **kwargs):
        super(Test, self).__init__(*args, **kwargs)
        self.frame = Tk()
        self.text_log = Text()
        self.ps_db = DatabaseMySLQ()
        self.ps_db.connect('127.0.0.1', 'root', '', 'prestashop')

    def test_requirements(self):
        def reqs():
            return [
                (gdr_prod['Nombre'], ([0], False, "La quantité de ce produit est à 0")),
                (gdr_prod['IDStock'], ([0, 1], True, "Ce produit ne peut pas être mis en vente"))
            ]

        gdr_prod = {
            'Nombre': 1,
            'IDStock': 0
        }
        c = Core(self.frame, Log(self.text_log))
        self.assertTrue(c.requirements(reqs()))

        gdr_prod['Nombre'] = 0
        self.assertFalse(c.requirements(reqs()))

        gdr_prod['IDStock'] = 7
        self.assertFalse(c.requirements(reqs()))
