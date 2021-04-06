# coding=utf-8
"""
filename: multiple_client_linux.py
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
sys.path.append("..")
from app.utils.login_handler import ProtocolDict
from app.utils.client import Client


class SockManager(object):
    clients = list()
    _running = 0
    __sockfd_message_queue_dict = dict()
    __sockfd_client_dict = dict()
    __lock = threading.Lock()
    __epoll = select.epoll()

    def __init__(self, clients, is_check_client_state=True):
        self.clients = clients
        self.is_check_client_state = is_check_client_state
        self.register_epoll()

    def register_epoll(self):
        for clt in self.clients:
            fd = clt.sock.fileno()
            self.__epoll.register(fd, select.EPOLLIN | select.EPOLLOUT)
            self.__sockfd_client_dict.update({fd: clt})
            self.__sockfd_message_queue_dict.update({fd: Queue.Queue()})
        print(self.__sockfd_client_dict)
        print(self.__sockfd_message_queue_dict)

    def say_hello(self):
        for clt in self.clients:
            clt.send_hello()

    def set_running(self, flag):
        self.__lock.acquire()
        self._running = flag
        self.__lock.release()

    def store_message(self, queue, message):
        queue.put(message)

    def get_message(self, queue):
        """
        :param queue:
        :return: {"client": xxx, "response": (protocol_type, protocol_instance)}
        """
        try:
            message = queue.get()
        except Queue.Empty:
            return None
        return message

    def check_state(self):
        for clt in self.clients:
            if clt.get_state() == 0:
                self.__sockfd_client_dict.pop(clt.sock)

    def heart_beat(self):
        while self._running:
            for clt in self.__sockfd_client_dict.itervalues():
                if clt.get_state():
                    action = ProtocolDict.get(0).get("action")
                    action(clt)
            time.sleep(8)

    def sock_manager(self):
        time.sleep(1)
        while self._running:
            events = self.__epoll.poll(1)
            if not events:
                continue
            #print("@@@@@@@@@@ ", events)
            for fd, event in events:
                clt = self.__sockfd_client_dict.get(fd)
                queue = self.__sockfd_message_queue_dict.get(fd)
                #print("************* one cycle start")
                if event & select.EPOLLIN:
                    #print("********* prepare to receive")
                    res = clt.receive()
                    if res[0] >= 0:
                        #print("$$$$$$$$$$$ {0} have received data".format(clt.login_name))
                        self.store_message(queue, (clt, res))
                    self.__epoll.modify(fd, select.EPOLLOUT)
                if event & select.EPOLLOUT:
                    #print("******* prepare to send")
                    message = self.get_message(queue)
                    self.message_handler(clt, message[1])
                    self.__epoll.modify(fd, select.EPOLLIN)
                #print("************ one cycle end")
        print("sock listener stop")

    def message_handler(self, client, response):
        protocol_type, protocol_instance = response
        if protocol_type < 0:
            return None
        handler_object_dict = ProtocolDict.get(protocol_type)
        if handler_object_dict is None:
            return None
        handler = handler_object_dict.get("handler")
        if handler is None:
            client.game_log("warn", protocol_type=protocol_type)
            return None
        handler(client, protocol_instance)

    def start(self):
        threads = list()
        tasks = [self.sock_manager, self.heart_beat]
        for task in tasks:
            threads.append(threading.Thread(target=task))
        self.set_running(1)
        self.say_hello()
        for th in threads:
            th.start()
        for th in threads:
            th.join()

    def stop(self):
        for clt in self.clients:
            clt.set_state(0)
            self.__epoll.unregister(clt.sock.fileno())
            self.set_running(0)
        self.__epoll.close()


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


if __name__ == "__main__":
    config = read_config()
    module = importlib.import_module("app.function." + config.get("function_name"))
    ProtocolDict = module.ProtocolDict
    test_clients = list()
    for i in range(config.get("min_name_index"), config.get("max_name_index")):
        test_clients.append(Client(config.get("server_id"), "fly"+str(i), 0))
    print("create client", [c.login_name for c in test_clients])
    sm = SockManager(test_clients, config.get("check_client_state"))
    sm.start()

