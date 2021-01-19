from Database import Database
import pymysql


class DatabaseMySLQ(Database):
    def connect(self, ip, login, pwd, name):
        """
        Connects to a MySQL Database
        :param ip: IP of the server
        :param login: Login of the user of the Database
        :param pwd: Password of the user of the Database
        :param name: Name of the Database
        :return: Logs,True|False if connection is successful or not
        """
        try:
            self.DB = pymysql.connect(host=ip, user=login, password=pwd, database=name)
            return "Connection successful", True
        except pymysql.err.OperationalError as OEr:
            return f"{OEr.args[1]}", False
