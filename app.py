from hashlib import md5
import os
from time import strftime
from uuid import uuid4
from flask import Flask, request, jsonify, session, make_response
from loguru import logger
from handler import CastlingHandler
from util import read_config, MyRSA

app = Flask(__name__)

logger.add(f"logs/{strftime('%Y-%m-%d')}.log",
            rotation="500MB",
            encoding="utf-8",
            enqueue=True,
            retention="5 days")

config = read_config()
if config["mod_name"] == "Castling":
    handler = CastlingHandler(config, True)

if "session_sec_key" not in config.keys() or config["session_sec_key"] == "":
    app.config["SECRET_KEY"] = os.urandom(24)
else:
    app.config["SECRET_KEY"] = config["session_sec_key"]

# app.config["WTF_CSRF_CHECK_DEFAULT"] = False


@app.route('/')
def hello():
    return 'Hello castling'

if not config["close_insert_pubkey"]:
    @app.route('/insert_pubkey', methods=["POST"])
    def insert_pubkey():
        ip = request.remote_addr
        logger.debug(f"ip:{ip}")
        if request.is_json:
            data = request.get_json(silent=True)
            from_local = ip == "127.0.0.1"
            from_admin = "admin_token" in request.json and config[
                "admin_token"] != "" and data["admin_token"] == config[
                    "admin_token"]
            if from_local or from_admin:
                uid = str(data["uid"])
                pubkey = str(data["pubkey"])
                logger.debug(f"uid:{uid}")
                logger.debug(f"pubkey:{pubkey}")
                handler.insert_pubkey_db(uid, pubkey)
                return jsonify({"status": "success"})
            return jsonify({
                "status": "failure",
                "error_msg": "not from localhost or admin"
            })
        return jsonify({"status": "failure", "error_msg": "data are not json"})


# @app.route('/login_pubs', methods=["POST"])
# def login_pubs():
#     session["valid"] = False
#     if request.is_json:
#         logger.debug(f"{request.data}")
#         data = request.get_json(silent=True)
#         if "ds" in data.keys():
#             for d in data["ds"]:
#                 d = str(d)
#                 if d == session["m"]:
#                     session["valid"] = True
#                     return jsonify({"status": "success"})
#             return jsonify({"status": "failure", "error_msg": "login failed"})
#         elif "uid" in data.keys():
#             # 设置明文给客户端
#             session["m"] = md5(str(uuid4()).encode()).hexdigest()
#             uid = str(data["uid"])
#             pubkeys = handler.search_pubkey_db(uid)
#             rsa = MyRSA(pubkeys)
#             es = rsa.encrypt_all(session["m"])
#             # 我不知道合理返回list[bytes]
#             # logger.debug(f"es: {bytes(es)}")
#             return make_response(bytes(es))
#     return jsonify({"status": "failure", "error_msg": "login failed"})


@app.route('/login', methods=["POST"])
def login():
    session["valid"] = False
    if request.is_json:
        logger.debug(f"{request.data}")
        data = request.get_json(silent=True)
        if "d" in data.keys():
            d = data["d"]
            if d == session["m"]:
                session["valid"] = True
                return jsonify({"status": "success"})
            return jsonify({"status": "failure", "error_msg": "login failed"})
        elif "uid" in data.keys():
            # 设置明文给客户端
            session["m"] = md5(str(uuid4()).encode()).hexdigest()
            logger.debug(f"Msg: {session['m']}")
            uid = str(data["uid"])
            pubkey = handler.search_pubkey_db(uid)
            rsa = MyRSA(pubkey)
            es = rsa.encrypt(session["m"])
            # logger.debug(f"es: {bytes(es)}")
            return make_response(es)
    return jsonify({"status": "failure", "error_msg": "login failed"})


@app.route('/search_key_by_key', methods=["GET"])
def search_key_by_key():
    if session["valid"]:
        key = request.args.get("key")
        res = handler.search_key_by_key(key)
        return jsonify(res)
    return jsonify({"status": "failure", "error_msg": "didn't login"})


@app.route('/search_key_by_name', methods=["GET"])
def search_key_by_name():
    if session["valid"]:
        name = request.args.get("name")
        res = handler.search_key_by_name(name)
        return jsonify(res)
    return jsonify({"status": "failure", "error_msg": "didn't login"})


@app.route('/search_id_by_name', methods=["GET"])
def search_id_by_name():
    if session["valid"]:
        name = request.args.get("name")
        res = handler.search_id_by_name(name)
        return jsonify(res)
    return jsonify({"status": "failure", "error_msg": "didn't login"})


@app.route('/give_id_key', methods=["GET"])
def give_id_key():
    if session["valid"]:
        id_person = request.args.get("id")
        key = request.args.get("key")
        cls = request.args.get("cls")
        kwargs = {}
        if "dst" in request.args.keys():
            kwargs["dst"] = request.args.get("dst")
        if "num" in request.args.keys():
            kwargs["num"] = int(request.args.get("num"))
        res = handler.give_id_key(id_person, key, cls, **kwargs)
        return jsonify(res)
    return jsonify({"status": "failure", "error_msg": "didn't login"})


@app.route('/delete_id_key', methods=["GET"])
def delete_id_key():
    if session["valid"]:
        id_person = request.args.get("id")
        key = request.args.get("key")
        kwargs = {}
        if "num" in request.args.keys():
            kwargs["num"] = int(request.args.get("num"))
        res = handler.delete_id_key(id_person, key, **kwargs)
        return jsonify(res)
    return jsonify({"status": "failure", "error_msg": "didn't login"})


@app.route('/refresh_key', methods=["GET"])
def refresh_key():
    if session["valid"]:
        res = handler.refresh_db()
        return jsonify(res)
    return jsonify({"status": "failure", "error_msg": "didn't login"})


@app.route('/make_deal', methods=["GET"])
def make_deal():
    if session["valid"]:
        id_buyer = request.args.get("id_buyer")
        id_seller = request.args.get("id_seller")
        key = request.args.get("key")
        try:
            price = float(request.args.get("price"))
        except Exception as e:
            return jsonify({"status": "failure", "error_msg": e})
        res = handler.make_deal(id_buyer, id_seller, key, price)
        return jsonify(res)
    return jsonify({"status": "failure", "error_msg": "didn't login"})


if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0', port=config["port"])
