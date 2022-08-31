import json


def read_config():
    config_path = 'config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    if "close_insert_pubkey" not in config.keys():
        config["close_insert_pubkey"] = True
    return config