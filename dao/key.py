from .sql_base import SqlBase

class KeyDB(SqlBase):
    def __init__(self, key_db_path, REGENERATE=True) -> None:
        super().__init__(key_db_path)
        if REGENERATE:
            self.create()

    def create(self):
        self.drop('Key')
        stmt = '''CREATE TABLE `Key`
        (`Key` TEXT PRIMARY KEY    NOT NULL,
        `Name` TEXT    NOT NULL,
        `Text` TEXT    NOT NULL,
        `Class` TEXT   NOT NULL,
        `NextKey` TEXT NOT NULL);'''
        self.execute(stmt)

    def insert_all_keys(self, colname_keys:tuple):
        colname = colname_keys[0] # tuple
        stmt = "INSERT OR REPLACE INTO `Key` ({}) VALUES ({})".format(','.join(colname), ','.join(["?"]*len(colname)))
        keys_name_text = colname_keys[1] # list
        self.executemany(stmt, keys_name_text)

    def fetchall_by_key(self, pattern:str):
        pattern = f'%{pattern}%'
        stmt = f"SELECT * FROM `Key` WHERE Key LIKE (?)"
        return self.fetchall(stmt, (pattern,))

    def fetchall_by_name(self, pattern:str):
        pattern = f'%{pattern}%'
        stmt = f"SELECT * FROM `Key` WHERE Name LIKE (?)"
        return self.fetchall(stmt, (pattern,))

    def fetchall_by_text(self, pattern:str):
        pattern = f'%{pattern}%'
        stmt = f"SELECT * FROM `Key` WHERE Text LIKE (?)"
        return self.fetchall(stmt, (pattern,))