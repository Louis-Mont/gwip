from unittest import TestCase
from Core.Core import Core
from gw_logging.Log import Log
from tkinter import Text, Tk


class Test(TestCase):
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
        frame = Tk()
        text_log = Text()
        c = Core(Log(text_log), frame)
        self.assertTrue(c.requirements(reqs()))

        gdr_prod['Nombre'] = 0
        self.assertFalse(c.requirements(reqs()))

        gdr_prod['IDStock'] = 7
        self.assertFalse(c.requirements(reqs()))
