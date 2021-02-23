from unittest import TestCase
from Core.Core import Core
from gw_logging.Log import Log
from tkinter import Text, Tk


class Test(TestCase):
    def test_requirements(self):
        gdr_prod = {'Nombre': 1}
        frame = Tk()
        text_log = Text()
        c = Core(Log(text_log), frame)
        self.assertTrue(c.requirements({gdr_prod['Nombre']: (0, "errmsg")}))
        gdr_prod['Nombre'] = 0
        self.assertFalse(c.requirements({gdr_prod['Nombre']: (0, "errmsg")}))

