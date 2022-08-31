import shutil
import xml.etree.ElementTree as et
from xml.dom import minidom
'''
slot=0 主武器
slot=1 副武器
slot=2 投掷物
slot=3 傻逼Jack跳过了
slot=4 傻逼Jack留空了
slot=5 护甲
class=0 主武器，副武器
class=1 投掷物
class=3 护甲，掉落物
'''
class2index = {
    '1stweapon': '0',
    '2stweapon': '0',
    'throwable': '1',
    'armor': '3',
    'drop': '3',
}


def restore(id_person: str):
    bak = f"{id_person}.bak"
    shutil.copyfile(bak, id_person)


def backup(id_person: str):
    bak = f"{id_person}.bak"
    shutil.copyfile(id_person, bak)


def add_item_stash_backpack(id_person: str, key: str, cls: str, dst: str,
                            num: int):
    '''
    id_person: absolute path of person file'''
    try:
        tree = et.parse(id_person)
    except et.ParseError:
        return "ParseError"
    except FileNotFoundError:
        return f"{id_person} not found"

    # 判断容量
    stash = tree.find(dst)
    capacity = int(stash.attrib["hard_capacity"])
    occupied = len(stash.getchildren())
    if occupied + num > capacity:
        return f"{dst.title()} capacity is not enough"

    item = et.Element("item", {
        "class": class2index[cls],
        "index": '-1',
        "key": key
    })
    for i in range(num):
        stash.append(item)

    tmp = et.tostring(tree.getroot(), encoding='unicode')
    lstr = minidom.parseString(tmp.replace('\n', '').replace(
        ' ' * 4, '')).toprettyxml(indent=" " * 4)
    with open(id_person, "w") as f:
        # with open("data/New_Database.xml", "w") as f:
        # logger.debug(lstr)
        f.write(lstr)
    return "success"


def delete_item_everywhere(id_person: str, key: str, num: int):
    '''
    id_person: absolute path of person file'''
    try:
        tree = et.parse(id_person)
    except et.ParseError:
        return "ParseError", 0
    except FileNotFoundError:
        return f"{id_person} not found", 0

    cnt = 0

    def write():
        nonlocal tree
        tmp = et.tostring(tree.getroot(), encoding='unicode')
        lstr = minidom.parseString(tmp.replace('\n', '').replace(
            ' ' * 4, '')).toprettyxml(indent=" " * 4)
        with open(id_person, "w") as f:
            # with open("data/New_Database.xml", "w") as f:
            f.write(lstr)

    # 搜索仓库和背包
    for cls in ["stash", "backpack"]:
        stash_back = tree.find(cls)
        for i in stash_back.findall("./item"):
            if i.attrib["key"] == key:
                stash_back.remove(i)
                cnt += 1
                if cnt >= num and num != -1:
                    write()
                    return "success", cnt

    # 搜索手中
    for i in tree.findall("item"):
        if i.attrib["key"] == key:
            i.attrib["index"] = "-1"
            i.attrib["amount"] = "0"
            i.attrib["key"] = ""
            cnt += 1
            if cnt >= num and num != -1:
                write()
                return "success", cnt

    write()
    return "success", cnt


def change_rp(id_person: str, inc_dec: float):
    '''
    id_person: absolute path of person file'''
    try:
        tree = et.parse(id_person)
    except et.ParseError:
        return "ParseError", 0
    except FileNotFoundError:
        return f"{id_person} not found", 0

    if isinstance(inc_dec, str):
        try:
            inc_dec = float(inc_dec)
        except:
            return f"{inc_dec} can't be cast to float", 0

    root = tree.getroot()

    old = float(root.attrib["job_points"])
    new = float(old) + inc_dec

    if new < 0:
        return f"get negative rp after operation", 0

    root.attrib["job_points"] = f"{new:.6f}"

    tmp = et.tostring(tree.getroot(), encoding='unicode')
    lstr = minidom.parseString(tmp.replace('\n', '').replace(
        ' ' * 4, '')).toprettyxml(indent=" " * 4)
    with open(id_person, "w") as f:
        # with open("New_Database.xml", "w") as f:
        # logger.debug(lstr)
        f.write(lstr)
    return "success", inc_dec


if __name__ == "__main__":
    id_person = r"D:\ProgramData\QQ\1692657550\FileRecv\profiles\2089573664.person"
    cls = "1stweapon"
    key = "m16a4.weapon"
    print(delete_item_everywhere(id_person, key, -1))

    # add_item_stash_backpack(id_person, key, cls)
    # print(change_rp(id_person, "-200"))
