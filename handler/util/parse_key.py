import xml.etree.ElementTree as et
from loguru import logger


def parse_text(mod_text_path: str = ""):
    global name2text
    if "name2text" in locals().keys():
        logger.debug("name2text has been defined")
        return
    name2text = {}
    # 读取翻译
    if len(mod_text_path) != 0:
        tree = et.parse(mod_text_path)
        for elem in tree.iter(tag="text"):
            key = elem.attrib["key"]
            try:
                text = elem.attrib["text"]
            except KeyError:
                continue
            name2text[key] = text


def parse_merged_weapon(merged_weapon_path: str, mod_text_path: str = ""):

    parse_text(mod_text_path)

    tree = et.parse(merged_weapon_path)

    global keys_name_text, existed
    existed = []
    keys_name_text = []
    for elem in tree.iter(tag="weapon"):
        key = elem.attrib['key']
        if 'ai' in key:
            continue
        if 'gk' not in key and 'ff' not in key:
            continue
        spec = elem.find('specification')

        name = spec.attrib['name']
        try:
            text = name2text[name]
        except KeyError:
            text = name
        if key in existed:
            continue
        keys_name_text.append((key, name, text))
        existed.append(key)
    logger.debug(f"一共搞了{len(keys_name_text)}把武器")
    return (("Key", "Name", "Text"), keys_name_text)


def parse_merged_carryitem(merged_carryitem_path: str, mod_text_path: str = ""):

    parse_text(mod_text_path)

    tree = et.parse(merged_carryitem_path)

    global keys_name_text, existed
    existed = []
    keys_name_text = []
    for elem in tree.iter(tag="carry_item"):
        key = elem.attrib['key']
        name = elem.attrib['name']
        try:
            text = name2text[name]
        except KeyError:
            text = name
        if key in existed:
            continue
        keys_name_text.append((key, name, text))
        existed.append(key)
    logger.debug(f"一共搞了{len(keys_name_text)}个物品")
    return (("Key", "Name", "Text"), keys_name_text)


def parse_all_key(mod_dir:str):
    mod_text_path = f"{mod_dir}/languages/cn/misc_text.xml"
    
    mod_items_dir = f"{mod_dir}/items"
    mod_weapon_dir = f"{mod_dir}/weapons"

    merged_weapon_path = mod_weapon_dir + r"/merged_weapon.weapon"
    merged_carryitem_path = mod_items_dir + r"/merged_carry_item.carry_item"
    # merged_valuable_path = mod_items_dir + r"/merged_valuable.valuable"

    column, k_n_t1 = parse_merged_weapon(merged_weapon_path, mod_text_path)
    column, k_n_t2 = parse_merged_carryitem(merged_carryitem_path, mod_text_path)
    # column, k_n_t3 = parse_merged_carryitem(merged_valuable_path, mod_text_path)
    
    return (column, k_n_t1+k_n_t2)
    
if __name__ == "__main__":
    mod_dir = r"E:/SteamLibrary/steamapps/workshop/content/270150/2606099273/media/packages/GFL_Castling"

    a, b = parse_all_key(mod_dir)
    c = 1
    