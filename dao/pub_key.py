from .sql_base import SqlBase


class PublicKey(SqlBase):
    def __init__(self, pub_key_db_path, REGENERATE=True) -> None:
        super().__init__(pub_key_db_path)
        if REGENERATE:
            self.create()

    def create(self):
        self.drop('PublicKey')
        stmt = '''CREATE TABLE `PublicKey`
        (`ID`       TEXT    NOT NULL,
        `Pubkey`    TEXT    NOT NULL,
        PRIMARY KEY(`ID`));'''
        # PRIMARY KEY(`ID`, `Pubkey`));'''
        self.execute(stmt)

    def insert_one(self, uid: str, pubkey: str):
        stmt = f"INSERT OR REPLACE INTO `PublicKey` (ID, Pubkey) VALUES (?, ?)"
        self.execute(stmt, (uid, pubkey))

    def select_all(self, uid:str):
        stmt = f"SELECT `Pubkey` FROM `PublicKey` WHERE ID = (?)"
        return self.fetchall(stmt, (uid,))