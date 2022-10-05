from .sql_base import SqlBase

class PersonDB(SqlBase):
    def __init__(self, person_db_path, REGENERATE=True) -> None:
        super().__init__(person_db_path)
        if REGENERATE:
            self.create()

    def create(self):
        self.drop('Person')
        stmt = '''CREATE TABLE `Person`
        (`ID` INTEGER PRIMARY KEY     NOT NULL,
        `XP`      REAL    NOT NULL,
        `RP`      REAL    NOT NULL);'''
        self.execute(stmt)

    def insert_all_persons(self, colname_persons:tuple):
        colname = colname_persons[0] # tuple
        stmt = f"INSERT OR REPLACE INTO `Person` ({','.join(colname)}) VALUES ({','.join(['?']*len(colname))})"
        persons_name_text = colname_persons[1] # list
        self.executemany(stmt, persons_name_text)

    def fetchall_by_id(self, id_person:str):
        stmt = f"SELECT * FROM `Person` WHERE ID = (?)"
        return self.fetchall(stmt, (id_person,))
