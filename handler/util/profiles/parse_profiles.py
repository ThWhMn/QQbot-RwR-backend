import os
import xml.etree.ElementTree as et
from xml.etree.ElementTree import ParseError
from loguru import logger

def parse_person(person_path:str):
    try:
        tree = et.parse(person_path)
    except ParseError:
        return None, None
    except FileNotFoundError:
        return None, None
    for person in tree.iter(tag="person"):
        xp = person.attrib['authority']
        rp = person.attrib['job_points']
    return xp, rp

def parse_all_person(profiles_folder_path:str):
    filename_name = []
    for file in os.scandir(profiles_folder_path):
        if file.name.endswith('.person'):
            xp, rp = parse_person(file.path)
            if xp is None:
                continue
            try:
                uid = int(file.name.replace('.person',''))
                filename_name.append((uid, xp, rp))
            except:
                logger.warning(f"{file.name} has something wrong")
    logger.debug(f"一共搞了{len(filename_name)}个角色仓库存档")
    return (("ID", "XP", "RP"), filename_name)

def parse_profile(profile_path:str):
    try:
        tree = et.parse(profile_path)
    except ParseError:
        return None
    except FileNotFoundError:
        return None
    for person in tree.iter(tag="profile"):
        username = person.attrib['username']
    return username

def parse_all_profile(profiles_folder_path:str):
    filename_name = []
    for file in os.scandir(profiles_folder_path):
        if file.name.endswith('.profile'):
            username = parse_profile(file.path)
            if username is None:
                continue
            try:
                uid = int(file.name.replace('.profile',''))
                filename_name.append((uid, username))
            except:
                logger.warning(f"{file.name} has something wrong")
    logger.debug(f"一共搞了{len(filename_name)}个角色资料存档")
    return (("ID", "Name"), filename_name)

if __name__ == "__main__":
    server_profiles_path= "D:/ProgramData/QQ/1692657550/FileRecv/profiles"
    server_profiles_path= r"E:\ProgramFiles\steamcmd\running_with_rifles_server\profiles"

    parse_all_person(server_profiles_path)