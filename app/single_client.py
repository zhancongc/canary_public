# coding=utf-8
"""
filename: single_client.py
author: zhancongc@icloud.com
description: 单客户端架构
"""
import sys
import time
import Queue
import select
import threading
import configparser
sys.path.append("..")
from app.utils.login_handler import ProtocolDict
from app.utils.client import Client


class Robot(object):
    client = None
    __message_queue = Queue.Queue()
    lock = threading.Lock()
    running = 0

    def __init__(self, server_id, login_name):
        self.client = Client(server_id, login_name)
        self.inputs = [self.client.sock]

    def set_running(self, flag):
        self.lock.acquire()
        self.running = flag
        self.lock.release()

    def store_message(self, message):
        self.__message_queue.put(message)

    def get_message(self):
        try:
            message = self.__message_queue.get(timeout=1)
        except Queue.Empty:
            return None
        return message

    def get_session_key(self):
        self.client.send_hello()
        res = self.client.receive_hello()
        if res[0] == -1:
            self.client.game_log("error", "cannot connect to server: {0}, because ".format(self.client.server, res[1]))
            sys.exit(0)
        self.client.game_log(log_type="info",
                             message="client {0} connected to server and get session key".format(
                                 self.client.login_name))
        handler = ProtocolDict.get(res[0]).get("handler")
        self.client.set_state(1)
        handler(self.client, res[1])

    def check_state(self):
        if self.client.get_state() == 0:
            if self.client.sock in self.inputs:
                self.inputs.remove(self.client.sock)
            self.client.close()

    def heart_beat(self):
        while self.running and self.inputs:
            action = ProtocolDict.get(0).get("action")
            action(self.client)
            time.sleep(1)

    def sock_listener(self):
        while self.running and self.inputs:
            readable, writeable, exceptional = select.select(self.inputs, [], [], 1)
            for _ in readable:
                res = self.client.receive()
                self.store_message({"client": self.client, "message": res})
            self.check_state()
        print("sock listener stop")

    def sock_handler(self):
        while self.running and self.inputs:
            response = self.get_message()
            if response:
                clt = response.get("client")
                protocol_type, protocol_instance = response.get("message")
                if self.client.is_logined:
                    if protocol_type not in [0, 4]:
                        self.client.response = protocol_type, protocol_instance
                    continue
                if protocol_type < 0:
                    continue
                handler_object_dict = ProtocolDict.get(protocol_type)
                if handler_object_dict is None:
                    continue
                handler = handler_object_dict.get("handler")
                if handler is None:
                    clt.game_log("warn", protocol_type=protocol_type)
                    continue
                handler(clt, protocol_instance)
            self.check_state()
        print("sock handler stop")

    def start(self):
        threads = list()
        tasks = [self.sock_listener, self.sock_handler, self.heart_beat]
        self.get_session_key()
        for task in tasks:
            threads.append(threading.Thread(target=task))
        self.set_running(1)
        for th in threads:
            th.start()
        while self.client.is_logined is False:
            time.sleep(0.1)
        print("check player logined")

    def stop(self):
        self.client.set_state(0)
        self.set_running(0)

    def send(self, protocol_type, parameter):
        self.client.send_pack(protocol_type, parameter)

    def get_response(self):
        time.sleep(0.1)
        return self.client.response


if __name__ == "__main__":
    conf = configparser.ConfigParser()
    try:
        conf.read("canary.ini")
        server_id = conf.getint("single", "server_id")
        login_name = conf.get("single", "login_name")
    except ValueError:
        print(ValueError)
        sys.exit(1)
    robot = Robot(server_id, login_name)
    robot.start()
    parameter = {"msg_type": 2, "zone_id": 0, "contact_player_name": "", "content": "Hello, world!",
                 "content_type_num": 1, "to_role_id": 0}
    robot.send(7801, parameter)
    time.sleep(2)
    print(robot.client.response)
    robot.stop()
