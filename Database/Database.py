from utils import dict_to_str, kcv
from abc import ABC, abstractmethod


class Database(ABC):
    def __init__(self):
        self.DB = None

    @abstractmethod
    def connect(self, *args):
        pass

    def __del__(self):
        if self.DB is not None:
            self.DB.close()

    def ii(self, table: str, values: dict, conditions: dict = None):
        """
        Inserts into the table the values using cur or Update if there is conditions
        :param table: The table you're inserting into
        :param values: The keys represent the titles and values the values inserted into said columns
        :param conditions: The names of the columns you're checking in n,0 and their values in n,1
        :return: False if there is no connection, True if the Insert Into/Update is successful
        """
        if self.DB is not None:
            self._ii(table, values, conditions)
            return True
        else:
            return False

    def _ii(self, table: str, values: dict, conditions: dict = None):
        cur = self.DB.cursor()
        if conditions is None:
            keys, values = dict_to_str(values)
            cur.execute(
                f"INSERT INTO {table} ({keys}) VALUES ({values})")
        else:
            # Update
            u_values = values.copy()
            for c in conditions:
                try:
                    u_values.pop(c)
                except KeyError:
                    pass
            # debug = f"UPDATE {table} SET {kcv(u_values, '=')} WHERE {kcv(conditions, '=', ' AND ')}"
            cur.execute(
                f"UPDATE {table} SET {kcv(u_values, '=')} WHERE {kcv(conditions, '=', ' AND ')}")
