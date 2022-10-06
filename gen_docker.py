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

container_name = "thwh_RWR"
img_name = "thwh_rwr_profile_server"
# 生成remove
rm_con = f"docker rm -f {container_name}\n"
rm_img = f"docker rmi {img_name}\n"

with open(remove, "w") as f:
    f.write(rm_con)
    f.write(rm_img)

# 生成run
pip_pack = "./data/packs"
if not os.path.exists(pip_pack):
    os.makedirs(pip_pack)
    pip_part = f"pip3 download -d {pip_pack} -r requirements.txt\n"
else:
    pip_part = ''

if run.endswith("bat"):
    build = ""
elif run.endswith("sh"):
    build = "chmod 777 run_remove.sh run_bak.sh\n"

build += f"docker build -t {img_name} .\n"
v_part = f"-v {mod_resource_path}:/mod -v {server_profiles_path}:/profiles"
v_part += f" -v {os.path.dirname(os.path.realpath(__file__))}/logs:/logs"
v_part += f" -v {os.path.dirname(os.path.realpath(__file__))}/data:/data"
run_dock = f"docker run -idt --name {container_name} -p {port}:{port} {v_part} {img_name}\n"

with open(run, "w") as f:
    f.write(pip_part)
    f.write(rm_con)
    f.write(rm_img)
    f.write(build)
    f.write(run_dock)

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
