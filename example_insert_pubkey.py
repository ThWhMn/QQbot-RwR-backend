import sys
import requests
from util import read_config

config = read_config()
def insert(uid, pubkey_path):
    url = f'http://127.0.0.1:{config["port"]}'+'/insert_pubkey'
    with open(pubkey_path, 'r') as f:
        pubkey = f.read()
    json_data = {
        "uid": uid,
        "pubkey": pubkey,
        "admin_token": config["admin_token"] if "admin_token" in config.keys() else ""
    }
    res = requests.post(url, json=json_data)
    print(res.json())

if __name__ == "__main__":
    if len(sys.argv) == 3:
        uid = sys.argv[1]
        pubkey_path = sys.argv[2]
    else:
        raise ValueError("something not defined, usage: python example_insert_pubkey.py username_or_uid path_to_pub_key")
    insert(uid, pubkey_path)