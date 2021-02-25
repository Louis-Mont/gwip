from tkinter import Tk

from Ui.Ui import Ui
from gw_logging.Log import Log
from Core.Core import Core

VERSION = '1.4.2 EXPERIMENTAL'

PS_DB = None
GDR_DB = None
C = None


def main():
    prestashop_ip = ui.ps_ip.get()
    prestashop_login = ui.ps_login.get()
    prestashop_pwd = ui.ps_password.get()
    prestashop_db_name = ui.ps_db_entry.get()
    dsn = ui.gdr_dsn.get()

    PS_DB, GDR_DB = C.connect(ui.gdr_dsn.get(), ui.ps_ip.get(), ui.ps_login.get(), ui.ps_password.get(),
                              ui.ps_db_entry.get())
    return PS_DB, GDR_DB


def on_closing(dbs, names):
    """
    When the main frame closes
    :param dbs: databases to be closed
    :param names: names of the databases, purely for logs
    """
    for i in range(len(dbs)):
        if dbs[i] is not None:
            dbs[i].close()
        print(f"{names[i]} database connection correctly closed")

    frame.destroy()


if __name__ == "__main__":
    frame = Tk()
    ui = Ui(frame, VERSION)
    i_log = Log(ui.log)
    C = Core(i_log, frame)

    ui.btn_addid.configure(
        command=lambda: C.add_id(int(ui.gdr_id.get()), ui.ps_cat_def.get(), ui.ps_title.get(), main()))
    ui.btn_resetdb.configure(command=lambda: C.reset_db(main()))
    ui.btn_syncventes.configure(command=lambda: C.syncventes(main()))

    # ui.btn_resetdb.grid_remove()
    frame.protocol("WM_DELETE_WINDOW", lambda: on_closing(
        [PS_DB, GDR_DB], ['Prestashop', 'GDR']))
    frame.mainloop()

    input("Press any key to quit...")
