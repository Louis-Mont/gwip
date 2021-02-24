from unittest import TestCase
from Core.Core import Core
from gw_logging.Log import Log
from tkinter import Text, Tk


class Test(TestCase):
    def test_requirements(self):
        gdr_prod = {
            'Nombre': 1,
            'IDSortie': 0
        }
        frame = Tk()
        text_log = Text()
        c = Core(Log(text_log), frame)
        reqs = {
            gdr_prod['Nombre']: ([0], False, "La quantité de ce produit est à 0"),
            gdr_prod['IDSortie']: ([0, 1], True, "Ce produit ne peut pas être mis en vente")
        }
        self.assertTrue(c.requirements(reqs))
        gdr_prod['Nombre'] = 0
        gdr_prod['IDSortie'] = 7
        reqs = {
            gdr_prod['Nombre']: ([0], False, "La quantité de ce produit est à 0"),
            gdr_prod['IDSortie']: ([0, 1], True, "Ce produit ne peut pas être mis en vente")
        }
        self.assertFalse(c.requirements(reqs))
