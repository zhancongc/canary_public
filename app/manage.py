# coding=utf-8
"""
filename: manage.py
author: zhancongc@icloud.com
description: 部分功能的web端展示
"""
import sys
import json
import time
from flask import Flask, render_template, request, jsonify
sys.path.append("..")
from app.utils.game_master import GameMaster
from app.all_servers import all_servers
from app.single_client import Robot

app = Flask(__name__)
app.config.update({"DEBUG": True})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/protocol")
def protocol():
    return render_template("protocol.html")


@app.route("/protocol_test", methods=["POST"])
def protocol_test():
    result = dict()
    server_id = request.form.get("server_id")
    login_name = request.form.get("login_name")
    protocol_name = request.form.get("protocol_name")
    parameter = request.form.get("parameter")
    if login_name is None or login_name == "":
        result.update({
            "state": 401,
            "msg": "login_name is None",
        })
        return jsonify(result)
    if server_id is None or server_id is u"":
        result.update({
            "state": 402,
            "msg": "server_id is None",
        })
        return jsonify(result)
    if protocol_name is None or protocol_name is u"":
        result.update({
            "state": 403,
            "msg": "protocol_name is None",
        })
        return jsonify(result)
    if parameter is None or parameter is u"":
        result.update({
            "state": 404,
            "msg": "parameter is None",
        })
        return jsonify(result)
    robot = Robot(int(server_id), login_name)
    robot.start()
    robot.send(int(protocol_name), json.loads(parameter))
    time.sleep(1)
    response = robot.client.response
    robot.stop()
    result.update({
        "state": 0,
        "msg": "ok",
        "data": str(response)
    })
    return jsonify(result)


@app.route("/sample")
def sample():
    return render_template("sample.html")


@app.route("/query")
def query():
    gm = GameMaster(all_servers.get(3000))
    res = gm.get_compile_time()
    gm.close()
    compile_time = json.loads(res)["data"]["compile_time"]
    return render_template("query.html", compile_time=compile_time)


@app.route("/query_by_role_id", methods=["POST"])
def query_open_id():
    result = dict()
    role_id = request.form.get("role_id")
    server_id = request.form.get("server_id")
    if role_id is None or role_id is u"":
        result.update({
            "state": 401,
            "msg": "role_id is None",
        })
        return jsonify(result)
    if server_id is None or server_id is u"":
        result.update({
            "state": 402,
            "msg": "server_id is None",
        })
        return jsonify(result)
    try:
        gm = GameMaster(all_servers.get(int(server_id)))
    except Exception as e:
        result.update({
            "state": 403,
            "msg": str(e)
        })
        return jsonify(result)
    res = gm.query_base_info_by_role_id(role_id=role_id)
    gm.close()
    res = json.loads(res)
    data = res.get("data")
    code = res.get("code")
    if code == 1:
        if data:
            result.update({
                "state": 0,
                "msg": "ok",
                "data": json.dumps(res.get('data'))
            })
            return jsonify(result)
    result.update({
        "state": 500,
        "msg": res.get('desc')
    })
    return jsonify(result)


@app.route("/superior_account")
def superior_account():
    return render_template("superior_account.html")


@app.route("/game_master")
def game_master():
    return render_template("game_master.html")


@app.route("/create_superior_account", methods=["POST"])
def create_superior_account():
    result = dict()
    server_id = request.form.get("server_id")
    login_name = request.form.get("login_name")
    robot = Robot(7, login_name)
    robot.start()
    robot.stop()
    gm = GameMaster(server_id)
    role_id = gm.query_base_info_by_login_name(login_name)
    gm.superior_account(role_id)
    gm.close()
    result.update({
        "state": 0,
        "msg": "请求完毕，请注册后登陆，检查是否创建成功"
    })
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
