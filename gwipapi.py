from prestapyt import PrestaShopWebServiceDict
from requests.auth import HTTPBasicAuth

from db_interface.DatabaseODBC import DatabaseODBC
from db_interface.DatabaseMySQL import DatabaseMySLQ
import requests

if __name__ == '__main__':
    # local
    key = "KKLSZNHGZI21FJQE3ZVR55F1JPLRW7VZ"
    url = "http://localhost:80/prestashop/api"
    ps = PrestaShopWebServiceDict(url, key)
    gdr = DatabaseODBC()
    gdr.connect("gdr")
    cur_gdr = gdr.DB.cursor()
    cur_gdr.execute("SELECT Photo FROM Produit WHERE IDProduit=3")
    photo = bytes(cur_gdr.fetchall()[0][0])
    prodschema = ps.get('products', options={'schema': 'blank'})['product']
    print(prodschema)
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
