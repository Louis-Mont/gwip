from tkinter import Tk

from prestapyt import PrestaShopWebServiceDict
from requests.auth import HTTPBasicAuth

from Api.Api import Api
from Ui.Ui import Ui
from db_interface.DatabaseODBC import DatabaseODBC
import requests

from gw_logging.Log import Log

VERSION = '1.4.3 EXPERIMENTAL'


def add_product():
    main().add_id(int(ui.gdr_id.get()), ui.ps_title.get(), ui.ps_cat_def.get())


def reset_db():
    main().reset_db()


def sync_ventes():
    main().sync_ventes()


def main():
    return Api(frame, i_log, ui.gdr_dsn.get(), f"http://{ui.ps_ip.get()}", ui.ps_db_entry.get())


def on_closing(names):
    """
    When the main frame closes
    :param names: names of the databases, purely for logs
    """
    for name in names:
        print(f"{name} database connection correctly closed")

    frame.destroy()


if __name__ == '__main__':
    # local
    # key = "KKLSZNHGZI21FJQE3ZVR55F1JPLRW7VZ"
    # url = "http://localhost:80/prestashop/"
    frame = Tk()
    ui = Ui(frame, VERSION)
    ui.change_to_api_ui()
    i_log = Log(ui.log)

    ui.btn_addid.configure(
        command=lambda: add_product())
    ui.btn_resetdb.configure(command=lambda: reset_db())
    ui.btn_syncventes.configure(command=lambda: sync_ventes())

    # ui.btn_resetdb.grid_remove()
    frame.protocol("WM_DELETE_WINDOW", lambda: on_closing(
        ['GDR']))
    frame.mainloop()

    input("Press any key to quit...")
    """ps = PrestaShopWebServiceDict(url, key)
    gdr = DatabaseODBC()
    gdr.connect("gdr")
    cur_gdr = gdr.DB.cursor()
    cur_gdr.execute("SELECT Photo FROM Produit WHERE IDProduit=3")
    photo = bytes(cur_gdr.fetchall()[0][0])
    prodschema = ps.get('products', options={'schema': 'blank'})['product']
    catschema = ps.get('categories', options={'schema': 'blank'})['category']
    # for k, v in prodschema.items():
    #    print(f"{k} : {v}")
    for k, v in ps.get('products', 3)['product'].items():
        print(f"{k} : {v}")"""

# for k, v in catschema.items():
#    print(f"{k} : {v}")
# print(ps.get('categories'))

# print(ps.get('products')['products']['product'])
# print(type(photo))
# print(ps.get('images/products'))
# print(ps.get('products', 1))
# files = {'image': (f"image-{1}.png", photo)}
# print(requests.get(f"{url}/images/products/{1}", auth=HTTPBasicAuth(key, '')))
# requests.post(f"{url}/images/products/{1}", files=files, auth=HTTPBasicAuth(key, ''))
# print(type(bytes(photo)))
"""
for k, v in ps.get('products').items():
    for title, p in v.items():
        for products in p:
            # print(products)
            print(ps.get('products', int(products['attrs']['id'])))
            """
