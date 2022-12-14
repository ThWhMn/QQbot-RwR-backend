from .util import parse_all_key, parse_all_person, parse_all_profile
from .util import add_item_stash_backpack, delete_item_everywhere, change_rp
from .util import restore, backup
from dao import KeyDB, PersonDB, ProfileDB
from loguru import logger
from .basic_hander import BasicHandler
import traceback


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
            ret["error_msg"] = traceback.format_exc()
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

    def group_keys(self, fetched: list):
        key2msg = {}
        for row in fetched:
            key2msg[row[0]] = row

        keys = list(key2msg.keys())
        ret = []
        while len(keys) != 0:
            key = keys.pop(0)
            nxt = key2msg[key][4]
            bucket = [key]
            while nxt != "" and nxt != key:
                bucket.append(nxt)
                keys.remove(nxt)
                nxt = key2msg[nxt][4]
            ret.append([key2msg[bucket[0]], [key2msg[k] for k in bucket]])

        return ret

    def search_key_by_key(self, key: str):
        logger.debug(f"search_key_by_key start, key: {key}")
        if not self.KEY_DONE:
            ret = self.failure_json.copy()
            ret["error_msg"] = "Key database not initialized"
            return ret

        ret1 = self.key_db.fetchall_by_key(key)
        # [()]
        if len(ret1) != 0 and ret1[0][4] != "":
            bucket = [ret1[0][0]]
            nxt = ret1[0][4]
            while nxt not in bucket:
                bucket.append(nxt)
                nxt = self.key_db.fetchall_by_key(nxt)
                ret1 += nxt
                nxt = nxt[0][4]
        ans = ret1

        ret = self.success_json.copy()
        ret["results"] = self.group_keys(ans)
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
        ret["results"] = self.group_keys(ans)
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
                msg = traceback.format_exc()
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
            ret = self.search_key_by_key(key)["results"][0][1]
            cnt = 0
            for item in ret:
                key = item[0]
                msg, tmp = delete_item_everywhere(id_person, key, num)
                cnt += tmp
                num -= tmp
                if msg != "success":
                    break

        except Exception as e:
            msg = traceback.format_exc()
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

    def make_deal(self, id_buyer: str, id_seller: str, key: str, price: float):
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
            ret = self.search_key_by_key(key)["results"][0][1]
            cnt = 0
            for item in ret:
                tmpkey = item[0]
                msg, tmp = delete_item_everywhere(id_seller, tmpkey, -1)
                cnt += tmp
                if msg != "success":
                    break
            logger.debug(
                f"delete_item_everywhere return: msg:{msg}, cnt:{cnt}")
            if msg == "success" and cnt == 0:
                msg = "??????????????????"
            if msg == "success":
                ret = self.success_json.copy()
                ret["results"] = f"????????????{cnt}?????????"
            else:
                restore(id_seller)
                ret = self.failure_json.copy()
                ret["error_msg"] = f"??????????????????????????????????????????????????????????????????{msg}"
                logger.debug(f"make_deal return, ret: {ret}")
                return ret
            msg, cnt = change_rp(id_seller, price)
            logger.debug(f"change_rp return: msg:{msg}, cnt:{cnt}")
            if msg == "success":
                ret["results"] += f"???????????????rp??????"
            else:
                restore(id_seller)
                ret = self.failure_json.copy()
                ret["error_msg"] = f"??????????????????????????????????????????rp??????????????????{msg}"
                logger.debug(f"make_deal return, ret: {ret}")
                return ret
        except Exception as e:
            restore(id_seller)
            ret = self.failure_json.copy()
            ret["error_msg"] = f"????????????????????????????????????????????????????????????{traceback.format_exc()}"
            logger.debug(f"make_deal return, ret: {ret}")
            return ret

        backup(id_buyer)
        try:
            msg = add_item_stash_backpack(id_buyer, key, "1stweapon",
                                          "backpack", 1)
            logger.debug(f"add_item_stash_backpack return: msg:{msg}")
            if msg == "success":
                ret["results"] += f"??????????????????1?????????"
            else:
                restore(id_seller)
                restore(id_buyer)
                ret = self.failure_json.copy()
                ret["error_msg"] = f"????????????????????????????????????????????????????????????????????????{msg}"
                logger.debug(f"make_deal return, ret: {ret}")
                return ret

            msg, cnt = change_rp(id_buyer, -price)
            logger.debug(f"change_rp return: msg:{msg}, cnt:{cnt}")
            if msg == "success":
                ret["results"] += f"???????????????rp??????"
            else:
                restore(id_seller)
                restore(id_buyer)
                ret = self.failure_json.copy()
                ret["error_msg"] = f"????????????????????????????????????????????????rp??????????????????{msg}"
                logger.debug(f"make_deal return, ret: {ret}")
                return ret
        except Exception as e:
            restore(id_seller)
            restore(id_buyer)
            ret = self.failure_json.copy()
            ret["error_msg"] = f"??????????????????????????????????????????????????????????????????{traceback.format_exc()}"
            logger.debug(f"make_deal return, ret: {ret}")
            return ret
        return ret