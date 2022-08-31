import os
import xml.etree.ElementTree as et
from xml.etree.ElementTree import ParseError
from loguru import logger


def parse_person(person_path: str):
    try:
        tree = et.parse(person_path)
    except ParseError:
        return None
    for person in tree.iter(tag="person"):
        name = person.attrib['name']
    return name


def parse_all_person(profiles_folder_path: str):
    filename_name = []
    for file in os.scandir(profiles_folder_path):
        if file.name.endswith('.person'):
            name = parse_person(file.path)
            if name is None:
                continue
            filename_name.append((file.name.replace('.person', ''), name))
    logger.debug(f"一共搞了{len(filename_name)}个角色仓库存档")
    return (("ID", "Name"), filename_name)


person_keys = {
    "XP": "authority",  # 乘10000
    "RP": "job_points",
}
profile_stats = {
    "杀敌数": "kills",
    "阵亡数": "deaths",
    "游玩时间": "time_played",
    "击杀友军": "teamkills",
    "最长连杀": "longest_kill_streak",
    "摧毁目标": "targets_destroyed",
    "击毁载具": "vehicles_destroyed",
    "治疗士兵": "soldiers_healed",
    "移动距离": "distance_moved",
    "开火次数": "shots_fired",
    "投掷物品": "throwables_thrown",
}


def parse_profile(profile_path: str):
    try:
        tree = et.parse(profile_path)
    except ParseError:
        return None
    profile_attr = {}
    profile = tree.getroot()
    profile_attr["游戏昵称"] = profile.attrib["username"]
    stats = profile.find('stats')
    for k, v in profile_stats.items():
        profile_attr[k] = stats.attrib[v]


def parse_person_profile(profiles_folder_path: str):
    '''
    处理person文件和profile文件的玩家信息
    '''
    for file in os.scandir(profiles_folder_path):
        if file.name.endswith('.profile'):
            parse_all_person()


if __name__ == "__main__":
    server_profiles_path = "D:/ProgramData/QQ/1692657550/FileRecv/profiles"

    parse_all_person(server_profiles_path)