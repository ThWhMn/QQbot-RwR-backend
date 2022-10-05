from .util import parse_all_key, parse_all_person, parse_all_profile
from .util import add_item_stash_backpack, delete_item_everywhere, change_rp
from .util import restore, backup
from dao import KeyDB, PersonDB, ProfileDB
from loguru import logger
from .basic_hander import BasicHandler


class CastlingHandler(BasicHandler):
    def __init__(self, config: dict, REGENERATE=True) -> None:
        super().__init__(config, REGENERATE)

        # self.merged_w_path = self.resource_path + '/weapons/merged_weapon.weapon'
        # self.misc_txt_path = self.resource_path + '/languages/cn/misc_text.xml'
        self.KEY_DONE = False
        self.PERSON_DONE = False
        self.PROFILE_DONE = False
        self.make_key_db()
        self.make_person_db()
        self.make_profile_db()

    def refresh_db(self):
        try:
            logger.debug("refresh_db start")
            self.KEY_DONE = False
            self.PERSON_DONE = False
            self.PROFILE_DONE = False
            self.make_key_db()
            self.make_person_db()
            self.make_profile_db()
            logger.debug("Database refresh successfully")
            self.KEY_DONE = True
            self.PERSON_DONE = True
            self.PROFILE_DONE = True
            ret = self.success_json.copy()
            logger.debug(f"refresh_db return: {ret}")
            return ret
        except Exception as e:
            ret = self.failure_json.copy()
            ret["error_msg"] = e
            logger.debug("Database refresh failed")
            logger.debug(f"refresh_db return: {ret}")
            return ret

    def make_key_db(self):
        self.key_db = KeyDB(self.key_db_path, self.REGENERATE)
        self.colname_keys = parse_all_key(self.resource_path)
        self.key_db.insert_all_keys(self.colname_keys)
        logger.debug("Key database built successfully")
        self.KEY_DONE = True

    def make_person_db(self):
        self.person_db = PersonDB(self.person_db_path, self.REGENERATE)
        self.colname_persons = parse_all_person(self.profiles_path)
        self.person_db.insert_all_persons(self.colname_persons)
        logger.debug("Person database built successfully")
        self.PERSON_DONE = True

    def make_profile_db(self):
        self.profile_db = ProfileDB(self.profile_db_path, self.REGENERATE)
        self.colname_profiles = parse_all_profile(self.profiles_path)
        self.profile_db.insert_all_profiles(self.colname_profiles)
        logger.debug("Profile database built successfully")
        self.PROFILE_DONE = True

    def search_key_by_key(self, key: str):
        logger.debug(f"search_key_by_key start, key: {key}")
        if not self.KEY_DONE:
            ret = self.failure_json.copy()
            ret["error_msg"] = "Key database not initialized"
            return ret

        ret1 = self.key_db.fetchall_by_key(key)
        ans = list(ret1)

        ret = self.success_json.copy()
        ret["results"] = ans
        logger.debug(f"search_key_by_name return, ret: {ret}")
        return ret

    def search_key_by_name(self, name: str):
        logger.debug(f"search_key_by_name start, name: {name}")
        if not self.KEY_DONE:
            ret = self.failure_json.copy()
            ret["error_msg"] = "Key database not initialized"
            return ret

        ret1 = self.key_db.fetchall_by_name(name)
        ret2 = self.key_db.fetchall_by_text(name)
        ans = list(ret1 + ret2)

        ret = self.success_json.copy()
        ret["results"] = ans
        logger.debug(f"search_key_by_name return, ret: {ret}")
        return ret

    def search_id_by_name(self, name: str):
        logger.debug(f"search_id_by_name start, name: {name}")
        if not self.PROFILE_DONE:
            ret = self.failure_json.copy()
            ret["error_msg"] = "Profile database not initialized"
            return ret

        ret1 = self.profile_db.fetchall_by_name(name)
        ans = list(ret1)

        ret = self.success_json.copy()
        ret["results"] = ans
        logger.debug(f"search_id_by_name return, ret: {ret}")
        return ret

    def give_id_key(self,
                    id_person: str,
                    key: str,
                    cls: str,
                    dst: str = "backpack",
                    num: int = 1):
        logger.debug("give_id_key start, args: {}".format({
            'id_person': id_person,
            'key': key,
            'cls': cls,
            'dst': dst,
            'num': num
        }))
        if dst in ["stash", "backpack"]:
            if not id_person.endswith(".person"):
                id_person += ".person"
            id_person = self.profiles_path + '/' + id_person
            backup(id_person)
            try:
                msg = add_item_stash_backpack(id_person, key, cls, dst, num)
            except Exception as e:
                msg = e
            if msg == "success":
                ret = self.success_json.copy()
                logger.debug(f"give_id_key return, ret: {ret}")
                return ret
            else:
                restore(id_person)
                ret = self.failure_json.copy()
                ret["error_msg"] = msg
                logger.debug(f"give_id_key return, ret: {ret}")
                return ret
        else:
            restore(id_person)
            ret = self.failure_json.copy()
            ret["error_msg"] = "Destination error, not stash or backpack"
            logger.debug(f"give_id_key return, ret: {ret}")
            return ret

    def delete_id_key(self, id_person: str, key: str, num: int = 1):
        logger.debug("delete_id_key start, args: {}".format({
            'id_person': id_person,
            'key': key,
            'num': num
        }))
        if not id_person.endswith(".person"):
            id_person += ".person"
        id_person = self.profiles_path + '/' + id_person
        backup(id_person)
        try:
            msg, cnt = delete_item_everywhere(id_person, key, num)
        except Exception as e:
            msg = e
        if msg == "success":
            ret = self.success_json.copy()
            ret["results"] = cnt
            logger.debug(f"delete_id_key return, ret: {ret}")
            return ret
        else:
            restore(id_person)
            ret = self.failure_json.copy()
            ret["error_msg"] = msg
            logger.debug(f"delete_id_key return, ret: {ret}")
            return ret

    def make_deal(self, id_buyer:str, id_seller:str, key:str, price:float):
        logger.debug("make_deal start, args: {}".format({
            'id_buyer': id_buyer,
            'id_seller': id_seller,
            'key': key,
            'price': price
        }))
        if not id_buyer.endswith(".person"):
            id_buyer += ".person"
        if not id_seller.endswith(".person"):
            id_seller += ".person"

        id_buyer = self.profiles_path + '/' + id_buyer
        id_seller = self.profiles_path + '/' + id_seller
        backup(id_seller)
        try:
            # logger.debug(f"delete_item_everywhere start: id_seller:{id_seller}, key:{key}")
            msg, cnt = delete_item_everywhere(id_seller, key, -1)
            logger.debug(f"delete_item_everywhere return: msg:{msg}, cnt:{cnt}")
            if cnt == 0:
                msg = "卖家没有武器"
            if msg == "success":
                ret = self.success_json.copy()
                ret["results"] = f"删除卖家{cnt}把武器"
            else:
                restore(id_seller)
                ret = self.failure_json.copy()
                ret["error_msg"] = f"已恢复卖家存档，因在删除卖家武器时出现错误：{msg}"
                logger.debug(f"make_deal return, ret: {ret}")
                return ret
            msg, cnt = change_rp(id_seller, price)
            logger.debug(f"change_rp return: msg:{msg}, cnt:{cnt}")
            if msg == "success":
                ret["results"] += f"，增加卖家rp成功"
            else:
                restore(id_seller)
                ret = self.failure_json.copy()
                ret["error_msg"] = f"已恢复卖家存档，因在添加卖家rp时出现错误：{msg}"
                logger.debug(f"make_deal return, ret: {ret}")
                return ret
        except Exception as e:
            restore(id_seller)
            ret = self.failure_json.copy()
            ret["error_msg"] = f"已恢复卖家存档，因在处理卖家时出现错误：{e}"
            logger.debug(f"make_deal return, ret: {ret}")
            return ret

        backup(id_buyer)
        try:
            msg = add_item_stash_backpack(id_buyer, key, "1stweapon", "stash", 1)
            logger.debug(f"add_item_stash_backpack return: msg:{msg}")
            if msg == "success":
                ret["results"] += f"，给买家发放1把武器"
            else:
                restore(id_seller)
                restore(id_buyer)
                ret = self.failure_json.copy()
                ret["error_msg"] = f"已恢复买卖双方存档，因在发放买家武器时出现错误：{msg}"
                logger.debug(f"make_deal return, ret: {ret}")
                return ret

            msg, cnt = change_rp(id_buyer, -price)
            logger.debug(f"change_rp return: msg:{msg}, cnt:{cnt}")
            if msg == "success":
                ret["results"] += f"，扣除买家rp成功"
            else:
                restore(id_seller)
                restore(id_buyer)
                ret = self.failure_json.copy()
                ret["error_msg"] = f"已恢复买卖双方存档，因在扣除买家rp时出现错误：{msg}"
                logger.debug(f"make_deal return, ret: {ret}")
                return ret
        except Exception as e:
            restore(id_seller)
            restore(id_buyer)
            ret = self.failure_json.copy()
            ret["error_msg"] = f"已恢复买卖双方存档，因在处理买家时出现错误：{e}"
            logger.debug(f"make_deal return, ret: {ret}")
            return ret
        return ret