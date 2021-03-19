from tkinter import Tk
from Api.Api import Api
from Ui.Ui import Ui

from gw_logging.Log import Log

VERSION = '1.5.3-alpha'


def add_product():
    try:
        main().add_id(int(ui.gdr_id.get()), ui.ps_title.get(), ui.ps_cat_def.get())
    except ValueError:
        i_log.add("L'ID du Produit n'est pas un entier")


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
    # key = "DKG6MFPXV7EHY83JQL5RSL7PZYDWKL21"
    frame = Tk()
    ui = Ui(frame, VERSION)
    ui.change_to_api_ui()
    i_log = Log(ui.log)

    ui.btn_addid.configure(command=lambda: add_product())
    ui.btn_resetdb.configure(command=lambda: reset_db())
    ui.btn_syncventes.configure(command=lambda: sync_ventes())

    # ui.btn_resetdb.grid_remove()
    frame.protocol("WM_DELETE_WINDOW", lambda: on_closing(['GDR']))
    frame.mainloop()

    input("Press any key to quit...")
