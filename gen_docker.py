import json
import os
import platform
import shutil
from util import read_config

if os.path.exists("config_bak.json"):
    shutil.copy("config_bak.json", "config.json")
else:
    shutil.copy("config.json", "config_bak.json")

config = read_config()
port = config["port"]
mod_resource_path = config["mod_resource_path"]
server_profiles_path = config["server_profiles_path"]

if platform.system() == "Windows":
    remove = "run_remove.bat"
    run = "run.bat"
    bak = "run_bak.bat"
elif platform.system() == "Linux":
    remove = "run_remove.sh"
    run = "run.sh"
    bak = "run_bak.sh"

# 生成remove
rm_con = "docker rm -f RWR\n"
rm_img = "docker rmi rwr_profile_server\n"

with open(remove, "w") as f:
    f.write(rm_con)
    f.write(rm_img)

# 生成run
if run.endswith("bat"):
    build = ""
elif run.endswith("sh"):
    build = "chmod 777 run_remove.sh run_bak.sh\n"

build += "docker build -t rwr_profile_server .\n"
v_part = f"-v {mod_resource_path}:/mod -v {server_profiles_path}:/profiles"
v_part += f" -v {os.path.dirname(os.path.realpath(__file__))}/logs:/logs"
v_part += f" -v {os.path.dirname(os.path.realpath(__file__))}/data:/data"
rundo = f"docker run -idt --name RWR -p {port}:{port} {v_part} rwr_profile_server\n"

with open(run, "w") as f:
    f.write(rm_con)
    f.write(rm_img)
    f.write(build)
    f.write(rundo)

with open("config.json", "w") as f:
    config["mod_resource_path"] = "/mod"
    config["server_profiles_path"] = "/profiles"
    json.dump(config, f, indent=4)

# 生成run_bak
with open(bak, "w") as f:
    if bak.endswith("bat"):
        f.write("copy config_bak.json config.json")
    elif bak.endswith("sh"):
        f.write("cp config_bak.json config.json")
