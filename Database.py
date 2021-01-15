import pymysql
import pypyodbc


class Database:
    def __init__(self):
        self.DB = None

    def mysql_connect(self, ip: str, login: str, pwd: str, name: str):
        try:
            self.DB = pymysql.connect(ip, login, pwd, name)
            return "Connection successful", True
        except pymysql.err.OperationalError as OEr:
            return f"{OEr.args[1]}", False

    def dns_connect(self, dsn: str):
        self.DB = pypyodbc.connect(f"DSN={dsn};")
        return True

    def __del__(self):
        if self.DB is not None:
            self.DB.close()
