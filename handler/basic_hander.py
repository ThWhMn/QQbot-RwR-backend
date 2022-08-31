import json
from dao import PublicKey


class BasicHandler():
    def __init__(self, config: dict, REGENERATE: bool) -> None:
        self.config = config
        self.check_config()
        self.REGENERATE = REGENERATE
        self.success_json = {"status": "success"}
        self.failure_json = {"status": "failure", "error_msg": ""}
        self.make_pubkey_db()

    def check_config(self):
        # 绝不为空
        if len(self.config["mod_resource_path"]) == 0:
            raise ValueError("mod_resource_path not set")
        if len(self.config["server_profiles_path"]) == 0:
            raise ValueError("server_profiles_path not set")

        self.resource_path = self.config["mod_resource_path"]
        self.profiles_path = self.config["server_profiles_path"]

        # 可以为空
        # key_db_path
        if "key_db_path" not in self.config.keys():
            self.key_db_path = "./data/key.db"
        else:
            self.key_db_path = self.config["key_db_path"]
        # profile_db_path
        if "profile_db_path" not in self.config.keys():
            self.profile_db_path = "./data/profile.db"
        else:
            self.profile_db_path = self.config["profile_db_path"]
        # person_db_path
        if "person_db_path" not in self.config.keys():
            self.person_db_path = "./data/person.db"
        else:
            self.person_db_path = self.config["person_db_path"]
        # pub_key_db_path
        if "pub_key_db_path" not in self.config.keys():
            self.pub_key_db_path = "./data/pub_key.db"
        else:
            self.pub_key_db_path = self.config["pub_key_db_path"]
        # pub_key_json
        if "pub_key_json" not in self.config.keys():
            self.pub_key_json = "./data/pub_key.json"
        else:
            self.pub_key_json = self.config["pub_key_json"]

    def make_pubkey_db(self):
        self.pubkey_db = PublicKey(self.pub_key_db_path, self.REGENERATE)
        with open(self.pub_key_json, 'r', encoding='utf-8') as f:
            pk_json = json.load(f)
            for uid, pubkey in pk_json.items():
                self.insert_pubkey_db(uid, pubkey)

    def insert_pubkey_db(self, uid: str, pubkey: str):
        self.pubkey_db.insert_one(uid, pubkey)
        with open(self.pub_key_json, 'r', encoding='utf-8') as f:
            pk_json = json.load(f)
            pk_json[uid] = pubkey
        with open(self.pub_key_json, 'w', encoding='utf-8') as f:
            json.dump(pk_json, f, indent=4)
    
    def search_pubkey_db(self, uid:str ):
        pubkeys = self.pubkey_db.select_all(uid)
        pubkeys = [tup[0] for tup in pubkeys]
        return pubkeys
    