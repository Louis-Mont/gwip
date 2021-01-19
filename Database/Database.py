from utils import dict_to_str, kcv, l_to_str
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

    def df(self, table: str, n_conditions: tuple = None):
        """
        Delete all content from the table not in conditions
        :param table: The table you're deleting from
        :param n_conditions: The no conditions
        """
        if self.DB is not None:
            self._df(table, n_conditions)
            self.DB.commit()
            return True
        else:
            return False

    def _df(self, table: str, n_conditions: tuple = None):
        cur_ps = self.DB.cursor()
        if n_conditions is None:
            cur_ps.execute(f"DELETE FROM {table}")
        else:
            cur_ps.execute(f"DELETE FROM {table} WHERE {n_conditions[0]} NOT IN ({l_to_str(n_conditions[1])})")

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
            self.DB.commit()
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
