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

    item_tag = "item_group"
    occupied = 0
    children = list(stash)
    for child in children:
        if child.tag != item_tag:
            return f"Item tag is `{child.tag}` not `{item_tag}`. Fuck Jack"
        occupied += int(child.attrib["amount"])
    if occupied + num > capacity:
        return f"`{dst.title()}` capacity is not enough"

    handled_attr = ["class", "index", "key", "amount"]
    item = et.Element(item_tag, {
        "class": class2index[cls],
        "index": '-1',
        "key": key,
        "amount":  str(num),
    })

    # 检查物品项目的属性是否都定义正确
    if len(children) != 0:
        for attr in children[0].attrib:
            if attr in handled_attr:
                handled_attr.remove(attr)
            else:
                return f"`{item_tag}` has an attribute named `{attr}` but it has not been handled. Fuck Jack"
        if len(handled_attr) != 0:
            return "These attributes maybe removed from `{}`: {}. Fuck Jack".format(item_tag, ','.join(handled_attr))

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
        return f"ParseError in {id_person}", -1
    except FileNotFoundError:
        return f"{id_person} not found", -1
    if num == 0:
        return "success", 0

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
    for dst in ["stash", "backpack"]:
        stash_back = tree.find(dst)

        item_tag = "item_group"
        children = list(stash_back)

        for child in children:
            if child.tag != item_tag:
                return f"Item tag is `{child.tag}` not `{item_tag}`. Fuck Jack"
            if child.attrib["key"] == key:
                cnt += int(child.attrib["amount"])
                if cnt >= num and num > 0:
                    if cnt == num:
                        stash_back.remove(child)
                    else:
                        child.attrib["amount"] = str(cnt - num)
                    write()
                    return "success", cnt
                stash_back.remove(child)

    # 搜索手中
    for i in tree.findall("item"):
        if i.attrib["key"] == key:
            i.attrib["index"] = "-1"
            i.attrib["amount"] = "0"
            i.attrib["key"] = ""
            cnt += 1
            if cnt == num and num > 0:
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
    id_person = r"E:\ProgramFiles\steamcmd\running_with_rifles_server\profiles\2089573664.person"
    cls = "1stweapon"
    key = "m16a4.weapon"
    key = "medikit.weapon"
    print(delete_item_everywhere(id_person, key, -1))

    # print(add_item_stash_backpack(id_person, key, cls, dst="backpack", num=1))
    # print(add_item_stash_backpack(id_person, key, cls, dst="stash", num=1))
    # print(change_rp(id_person, "-200"))
