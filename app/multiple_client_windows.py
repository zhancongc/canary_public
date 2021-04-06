# coding=utf-8
"""
filename: multiple_client_windows.py
author: zhancongc@icloud.com
description: 多客户端架构
"""
import sys
import time
import Queue
import select
import threading
import importlib
import configparser
import multiprocessing
sys.path.append("..")
from app.utils.login_handler import ProtocolDict
from app.utils.client import Client


class SockManager(object):
    clients = list()
    _running = 0
    __inputs = list()
    __message_queue = Queue.Queue()
    __sockfd_client_dict = dict()
    __lock = threading.Lock()

    def __init__(self, clients, is_check_client_state=True):
        self.clients = clients
        self.is_check_client_state = is_check_client_state
        self.register_select()

    def set_running(self, flag):
        self.__lock.acquire()
        self._running = flag
        self.__lock.release()

    def store_message(self, message):
        self.__message_queue.put(message)

    def get_message(self):
        try:
            message = self.__message_queue.get(timeout=1)
        except Queue.Empty:
            return None
        return message

    def register_select(self):
        for clt in self.clients:
            self.__sockfd_client_dict.update({clt.sock.fileno(): clt})
            self.__inputs.append(clt.sock)

    def get_session_key(self):
        for clt in self.clients:
            clt.game_log("info", -1, "client {0} connected to server and get session key".format(clt.login_name))
            clt.send_hello()
            res = clt.receive_hello()
            if res[0] == -1:
                clt.game_log("error", "cannot connect to server: {0}, because ".format(clt.server, res[1]))
                sys.exit(0)
            clt.game_log(log_type="info",
                         message="client {0} connected to server and get session key".format(clt.login_name))
            handler = ProtocolDict.get(res[0]).get("handler")
            clt.set_state(1)
            handler(clt, res[1])

    def check_state(self):
        for clt in self.clients:
            if clt.get_state() == 0:
                if clt.sock in self.__inputs:
                    self.__inputs.remove(clt.sock)
                    self.__sockfd_client_dict.pop(clt.sock.fileno())

    def heart_beat(self):
        while self._running and self.__inputs:
            for clt in self.clients:
                if clt.get_state():
                    action = ProtocolDict.get(0).get("action")
                    action(clt)
            time.sleep(5)

    def sock_listener(self):
        while self._running and self.__inputs:
            readable, writeable, exceptional = select.select(self.__inputs, [], [], 1)
            for sock in readable:
                clt = self.__sockfd_client_dict.get(sock.fileno())
                if clt:
                    res = clt.receive()
                    self.store_message({"client": clt, "message": res})
            if self.is_check_client_state:
                self.check_state()
        print("sock listener stop")

    def sock_handler(self):
        while self._running and self.__inputs:
            response = self.get_message()
            if response:
                clt = response.get("client")
                protocol_type, protocol_instance = response.get("message")
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
            if self.is_check_client_state:
                self.check_state()
        print("sock handler stop")

    def start(self):
        threads = list()
        task = [self.sock_listener, self.sock_handler, self.heart_beat]
        self.get_session_key()
        for tk in task:
            threads.append(threading.Thread(target=tk))
        self.set_running(1)
        for th in threads:
            th.start()
        for th in threads:
            th.join()

    def stop(self):
        for clt in self.clients:
            clt.set_state(0)
            self.set_running(0)


def read_config():
    config = dict()
    conf = configparser.ConfigParser()
    try:
        conf.read("canary.ini")
        config.update({
            "server_id": conf.getint("multiple", "server_id"),
            "min_name_index": conf.getint("multiple", "min_name_index"),
            "max_name_index": conf.getint("multiple", "max_name_index"),
            "function_name": conf.get("multiple", "function_name"),
            "check_client_state": conf.getboolean("multiple", "check_client_state")
        })
    except ValueError:
        print(ValueError)
        sys.exit(1)
    return config


def group_by(start, end, steps=5):
    index = start
    arr = list()
    while index < end:
        arr1 = list()
        step = 0
        while step < steps:
            arr1.append(index + step)
            step += 1
        arr.append(arr1)
        index += steps
    return arr


def process_start():
    config = read_config()
    module = importlib.import_module("app.function." + config.get("function_name"))
    ProtocolDict = module.ProtocolDict
    group_list = group_by(config.get("min_name_index"), config.get("max_name_index"))
    process_list = list()
    for group in group_list:
        test_clients = list()
        for elem in group:
            test_clients.append(Client(config.get("server_id"), "fly"+str(elem)))
        print("create client", [c.login_name for c in test_clients])
        sm = SockManager(test_clients, config.get("check_client_state"))
        process = multiprocessing.Process(target=sm.start)
        process_list.append(process)
    for process in process_list:
        process.start()
        time.sleep(1)
    for process in process_list:
        process.join()
        time.sleep(1)


def simple_start():
    config = read_config()
    module = importlib.import_module("app.function." + config.get("function_name"))
    ProtocolDict = module.ProtocolDict
    test_clients = list()
    for index in range(config.get("min_name_index"), config.get("max_name_index")):
        test_clients.append(Client(config.get("server_id"), "fly"+str(index), 0))
    print("create client", [c.login_name for c in test_clients])
    sm = SockManager(test_clients, config.get("check_client_state"))
    sm.start()


if __name__ == "__main__":
    simple_start()



