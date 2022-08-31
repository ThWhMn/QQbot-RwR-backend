import asyncio
import hashlib
import requests as req
from handler import CastlingHandler
from util import read_config, MyRSA

# colname = [1,2,3]
# print(f"{','.join([r'%s']*len(colname))}")
# print({"results": [1,2]}.update({"a":[3,4]}))
# exit(0)

config = read_config()
# if config["mod_name"] == "Castling":
#     handler = CastlingHandler(config, False)
# print(handler.search_id_by_name("ab"))


class Test():
    def __init__(self) -> None:
        self.url = f"http://127.0.0.1:{config['port']}"
        self.ses = req.Session()

    def login(self):
        url = self.url + '/login'
        json_data = {
            "uid": 123,
        }
        res = self.ses.post(url, json=json_data)
        e = res.content

        with open('data/pubkeys/test', 'r') as f:
            prikey = f.read()
        rsa = MyRSA(prikey)
        d = rsa.decrypt(e).decode()
        json_data = {"d": d}
        res = self.ses.post(url, json=json_data)
        print(res.json())

    def insert(self):
        url = self.url + '/insert_pubkey'
        with open('data/pubkeys/test.pub', 'r') as f:
            pubkey = f.read()
        json_data = {
            "uid": 123,
            "pubkey": pubkey,
            "admin_token": config["admin_token"]
        }
        res = self.ses.post(url, json=json_data)
        if res.status_code == 200:
            print(res.json())
        else:
            print(res.status_code)

    def hello(self):
        url = self.url + '/'
        res = self.ses.get(url)
        print(res.text)

    def search_key_by_key(self):
        url = self.url + '/search_key_by_key'
        key = "excutioner"
        res = self.ses.get(url, params={"key": key})
        print(res.json())

    def search_key_by_name(self):
        url = self.url + '/search_key_by_name'
        name = "外骨骼"
        res = self.ses.get(url, params={"name": name})
        print(res.json())

    def search_id_by_name(self):
        url = self.url + '/search_id_by_name'
        name = "THWH"
        res = self.ses.get(url, params={"name": name})
        print(res.json())

    def give_id_key(self):
        url = self.url + '/give_id_key'
        id_person = "2089573664"
        key = "m16a4.weapon"
        cls = "1stweapon"
        num = "2"
        res = self.ses.get(url,
                           params={
                               "id": id_person,
                               "key": key,
                               "cls": cls,
                               "num": num
                           })
        print(res.json())

    def delete_id_key(self):
        url = self.url + '/delete_id_key'
        id_person = "2089573664"
        key = "m16a4.weapon"
        num = "-1"
        res = self.ses.get(url,
                           params={
                               "id": id_person,
                               "key": key,
                               "num": num
                           })
        print(res.json())

    def refresh_key(self):
        url = self.url + '/refresh_key'
        res = self.ses.get(url)
        print(res.json())

    def make_deal(self):
        url = self.url + '/make_deal'
        id_buyer = "2089567656"
        id_seller = "2089573664"
        key = "m16a4.weapon"
        price = "2"
        res = self.ses.get(url,
                           params={
                               "id_buyer": id_buyer,
                               "id_seller": id_seller,
                               "key": key,
                               "price": price
                           })
        print(res.json())


def test_all(self: Test):
    passed = ["login", "insert"]
    for i in dir(self):
        iv = getattr(self, i)
        if callable(iv) and not i.startswith('_'):
            if i in passed:
                continue
            print(f"Call {i}")
            getattr(self, i)()


if __name__ == "__main__":
    # s = "123"
    # print(tuple([s]))
    # exit(0)
    t = Test()
    # t.insert()
    t.login()
    # t.delete_id_key()
    t.make_deal()
    # test_all(t)