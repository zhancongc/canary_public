# coding=utf-8
"""
filename: login_handler.py
author: zhancongc@icloud.com
description: 登陆流程的封装
"""

import time
from app.utils.utils import md5sum

# Action ##################################################################################


class Action(object):

    def __init__(self):
        pass

    def GateAction(self, client):
        """
        密钥口令
        """
        print("{0} [send] hello".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        client.send_pack(-1, {})

    def SystemTickAction(self, client):
        client.send_pack(0, {})

    def LoginAction(self, client, *args):
        """5002
        登陆协议
        """
        loginname = args[0]
        timestamp = str(int(time.time()))
        fcm = "1"
        key = "L@KF9m$04UO2(_RP?8ZU&9n"
        strings = loginname.encode() + timestamp.encode() + fcm.encode() + key.encode()
        ticket = md5sum(strings, False)
        parameter = {
            "loginname": loginname, "platform_name": "android", "source": "1", "timestamp": timestamp,
            "fcm": 1, "ticket": ticket, "gopen_id": "123", "score": 0, "black_tag": 0,
            "ugc_tag": 0, "zone_id": client.server.get("zone_id")
        }
        client.send_pack(5001, parameter)

    def AccountCreateAction(self, client, *args):
        """5003
        创建账号
        """
        parameter = {
            "name": args[0],
            "country_id": args[1],
            "device_id": "james's device",
            "telecom_oper": "123"
        }
        client.send_pack(5003, parameter)

    def AccountLoadCharAction(self, client, *args):
        """5005
        获取账号信息
        """
        parameter = {
            "role_id": args[0], "client_version": "1.0.7.12", "telecom_oper": "1", "network": "1",
            "system_hardware": "1", "device_id": "1"
        }
        client.send_pack(5005, parameter)

    def RoleRenameAction(self, client, *args):
        parameter = {
            "new_name": args[0]
        }
        client.send_pack(7351, parameter)

    def RoleChooseCountryAction(self, client, *args):
        parameter = {
            "country_id": args[0]
        }
        client.send_pack(7351, parameter)


action = Action()


# Handler ################################################################################


class Handler(object):
    def __init__(self):
        pass

    def SystemTickHandler(self, client, protocol_instance):
        pass

    def GateHandler(self, client, protocol_instance):
        key = protocol_instance.key
        client.encrypt_instance_init(key)
        client.set_state(1)
        action.LoginAction(client, client.login_name)

    def ErrorCodeResultHandler(self, client, protocol_instance):
        pass

    def LoginHandler(self, client, protocol_instance):
        if protocol_instance.roles:
            role_id = protocol_instance.roles[0].id
            if role_id:
                client.role_id = role_id
                print("role_id: ", role_id)
                action.AccountLoadCharAction(client, role_id)
        elif protocol_instance.new_name:
            print("new_name", protocol_instance.new_name)
            action.AccountCreateAction(client, client.login_name, 1)

    def CreateResultHandler(self, client, protocol_instance):
        print("login_name", client.login_name)
        action.LoginAction(client, client.login_name)

    def AccountLoadCharHandler(self, client, protocol_instance):
        pass

    def CharLoadEndHandler(self, client, protocol_instance):
        client.is_logined = True
        print("login successfully")


handler = Handler()

ProtocolDict = {
    0: {"action": action.SystemTickAction},
    4: {"handler": handler.SystemTickHandler},
    98: {"handler": handler.ErrorCodeResultHandler},
    100: {"handler": handler.GateHandler},
    5001: {"action": action.LoginAction},
    5002: {"handler": handler.LoginHandler},
    5003: {"action": action.AccountCreateAction},
    5004: {"handler": handler.CreateResultHandler},
    5005: {"action": action.AccountLoadCharAction},
    5006: {"handler": handler.AccountLoadCharHandler},
    5018: {"handler": handler.CharLoadEndHandler}
}
