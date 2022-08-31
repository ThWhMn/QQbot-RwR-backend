import os
import sqlite3

class SqlBase():
    def __init__(self, db_path) -> None:
        if not os.path.exists(os.path.dirname(db_path)):
            os.mkdir(os.path.dirname(db_path))
        self.db = sqlite3.connect(db_path, check_same_thread=False)
    
    def drop(self, table:str):
        c = self.db.cursor()
        c.execute(f"DROP TABLE IF EXISTS `{table}`")
        self.db.commit()
        
    def execute(self, stmt:str, args:tuple=()):
        c = self.db.cursor()
        c.execute(stmt, args)
        self.db.commit()

    def executemany(self, stmt:str, data:list):
        c = self.db.cursor()
        c.executemany(stmt, data)
        self.db.commit()
    
    def fetchall(self, stmt:str, args:tuple):
        c = self.db.cursor()
        c.execute(stmt, args)
        return c.fetchall()
        