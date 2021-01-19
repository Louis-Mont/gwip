from Database import Database
import pypyodbc


class DatabaseODBC(Database):
    def connect(self, dsn: str):
        """
        Connects to a DSN
        :param dsn: The DSN you're accessing to
        :return: True if the connection is successful, False if it isn't
        """
        try:
            self.DB = pypyodbc.connect(f"DSN={dsn};")
            return True
        except pypyodbc.Error:
            return False
