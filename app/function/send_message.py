# coding=utf-8
"""
filename: send_message.py
author: zhancongc@icloud.com
description: 发送消息的并发测试脚本
"""
import sys
import time
import random
sys.path.append("..")
from app.utils.login_handler import Action, Handler, ProtocolDict


hello_messages = [
    u"大家好，我是机器人{0}。",
    u"机器人{0}，祝你大吉大利！",
    u"春风如意马蹄疾，一日看尽长安花。（{0}）",
    u"春花秋月何时了，往事知多少。（{0}）",
    u"我欲乘风归去，又恐琼楼玉宇。（{0}）",
    u"但愿人长久，千里共婵娟。（{0}）"
]


# Action ##################################################################################


class MyAction(Action):

    def AccountLoadCharAction(self, client, *args):
        """5005
        获取账号信息
        """
        parameter = {
            "role_id": args[0], "client_version": "1.0.7.12", "telecom_oper": "1", "network": "1",
            "system_hardware": "1", "device_id": "1"
        }
        client.send_pack(5005, parameter)

    def ChatMsgAction(self, client, *args):
        parameter = {"msg_type": 2, "zone_id": 0, "contact_player_name": "", "content": "Hello, world!",
                     "content_type_num": 1, "to_role_id": 0}
        client.send_pack(7801, parameter)


action = MyAction()


# Handler ################################################################################


class MyHandler(Handler):

    def CharLoadEndHandler(self, client, protocol_instance):
        client.is_logined = True
        print("login successfully")
        action.RoleRenameAction(client, client.login_name)
        msg = random.choice(hello_messages)
        print(msg.format(client.login_name))
        action.ChatMsgAction(client, msg.format(client.login_name))

    def ChatMsgHandler(self, client, protocol_instance):
        msg = random.choice(hello_messages)
        # print(msg.format(client.login_name), client.role_id)
        time.sleep(5)
        action.ChatMsgAction(client, msg.format(client.login_name))


handler = MyHandler()


ProtocolDict.update({
    5018: {"handler": handler.CharLoadEndHandler},
    7801: {"action": action.ChatMsgAction},
    7802: {"handler": handler.ChatMsgHandler},
})
