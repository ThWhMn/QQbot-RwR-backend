from .sql_base import SqlBase

class ProfileDB(SqlBase):
    def __init__(self, profile_db_path, REGENERATE=True) -> None:
        super().__init__(profile_db_path)
        if REGENERATE:
            self.create()

    def create(self):
        self.drop('Profile')
        stmt = '''CREATE TABLE `Profile`
        (`ID` TEXT PRIMARY KEY     NOT NULL,
        `Name`      TEXT    NOT NULL);'''
        self.execute(stmt)

    def insert_all_profiles(self, colname_profiles:tuple):
        colname = colname_profiles[0] # tuple
        stmt = f"INSERT OR REPLACE INTO `Profile` ({','.join(colname)}) VALUES ({','.join(['?']*len(colname))})"
        profiles_name_text = colname_profiles[1] # list
        self.executemany(stmt, profiles_name_text)

    def fetchall_by_name(self, pattern:str):
        pattern = f'%{pattern}%'
        stmt = f"SELECT * FROM `Profile` WHERE Name LIKE (?)"
        return self.fetchall(stmt, (pattern,))
