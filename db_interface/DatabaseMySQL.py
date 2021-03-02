from . import Database
import pymysql


class DatabaseMySLQ(Database.Database):
    def __init__(self):
        super().__init__()

    def connect(self, ip, login, pwd, name):
        """
        Connects to a MySQL db_interface
        :param ip: IP of the server
        :type ip: str
        :param login: Login of the user of the db_interface
        :type login: str
        :param pwd: Password of the user of the db_interface
        :type pwd: str
        :param name: Name of the db_interface
        :type name: str
        :return: Logs,True|False if connection is successful or not
        """
        try:
            self.DB = pymysql.connect(host=ip, user=login, password=pwd, database=name)
            return "Connection successful", True
        except pymysql.err.OperationalError as OEr:
            return f"{OEr.args[1]}", False
