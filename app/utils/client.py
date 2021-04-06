# coding=utf-8
"""
filename: client.py
author: zhancongc@icloud.com
description: 单客户端
"""
import os
import sys
import time
import socket
from google.protobuf.message import DecodeError
sys.path.append("..")
from app.all_servers import all_servers
from app.utils.utils import md5sum, int2bytes, bytes2int, Encrypt
from app.utils.protocol_manager import protocol_manager


class Client(object):
    _sock = None
    _is_encrypt = True
    _send_times = 1
    _state = 0
    _encrypt_instance = None
    _logdir = "static\\log\\" if sys.platform == "win32" else "/var/log/canary/test_log/"
    server = dict()
    role_id = 0
    response = None

    def __init__(self, server_id, login_name, block=True):
        """
        :param server_id: 服务端
        :param login_name: 登陆名
        :param block: 是否阻塞
        """
        self.server = all_servers.get(server_id)
        self.login_name = login_name
        self._logfile = "{0}{1}_{2}_{3}{4}".format(self._logdir, "client", self.login_name, str(time.time()), ".txt")
        self._sock = self.server_connect(block)
        self.clear_log()
        self.is_logined = False

    @property
    def sock(self):
        return self._sock

    def encrypt_instance_init(self, key):
        self._encrypt_instance = Encrypt(key) if self._is_encrypt else None

    def clear_log(self):
        if os.path.exists(self._logfile):
            with open(self._logfile, "r+") as fp:
                fp.seek(0)
                fp.truncate()
        else:
            os.mknod(self._logfile)

    def get_state(self):
        return self._state

    def set_state(self, _state):
        self._state = _state

    def server_connect(self, block):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.server.get("host"), self.server.get("work_port")))
            sock.setblocking(block)
            self.game_log("info", "server connected")
        except Exception as ConnectError:
            self.game_log("error", "cannot connect to server, because {0}".format(ConnectError))
            sys.exit(1)
        return sock

    def send_pack(self, protocol_type, parameters):
        if protocol_type == -1:
            self._sock.send(b'\x01\x00\x00\x00')
            return 100, "ok"
        protocol_instance = protocol_manager.get_protocol_instance(protocol_type)
        if protocol_instance is None:
            msg = "There is no protocol.{0}".format(protocol_type)
            return -400, msg
        setattr(protocol_instance, "type", protocol_type)
        try:
            for key in parameters:
                setattr(protocol_instance, key, parameters[key])
        except Exception as SetAttrError:
            return -401, SetAttrError
        instance_bytes = protocol_instance.SerializeToString()
        protocol_type_bytes = int2bytes(protocol_type)
        if self._is_encrypt:
            source_byte_data = protocol_type_bytes + instance_bytes
            md5_bytes = md5sum(source_byte_data, True)
            encrypt_data = self._encrypt_instance.encrypt(int2bytes(self._send_times) + md5_bytes + source_byte_data)
            length = len(encrypt_data) + 4
            send_data = int2bytes(length) + encrypt_data
        else:
            length = len(instance_bytes) + len(protocol_type_bytes) + 4
            send_data = int2bytes(length) + protocol_type_bytes + instance_bytes
        if protocol_type >= 0:
            self.game_log("send", protocol_type=protocol_type, protocol_instance=protocol_instance)
        self._send_times += 1
        self._sock.send(send_data)
        return 200, "ok"

    def game_log(self, log_type, message="", protocol_type=1, protocol_instance=None):
        """
        :log_type: send recv info warn error
        """
        if log_type in ["info", "warn", "error"]:
            log_content = "{0} [{1}] {2}".format(time.strftime("%Y-%m-%d %H:%M:%S"), log_type, message)
            with open(self._logfile, "a+") as fp:
                print >> fp, log_content
        if log_type in ["recv", "send"]:
            log_content = "{0} {1} [{2}] protocol_type: {3}, protocol_instance: ".format(
                time.strftime("%Y-%m-%d %H:%M:%S"), time.time(), log_type, protocol_type)
            with open(self._logfile, "a+") as fp:
                print >> fp, log_content
                print >> fp, protocol_instance

    def receive(self):
        response_length, msg = self.get_pack_length()
        if response_length < 0:
            return -1, "cannot receive response"
        try:
            body_length = response_length - 4
        except Exception as GetBodyLengthError:
            return -2, "cannot parse body_length, because {0}".format(GetBodyLengthError)
        return self.get_pack_body(body_length)

    def get_pack_body(self, body_length):
        try:
            body_data = self._sock.recv(body_length)
        except IOError:
            return -2, IOError
        protocol_type = bytes2int(body_data[:4])
        protocol_instance = protocol_manager.get_protocol_instance(protocol_type)
        if protocol_instance is None:
            return -4, "cannot find protocol instance of protocol type {0}".format(protocol_type)
        try:
            protocol_instance.ParseFromString(body_data[4:])
        except DecodeError:
            return -5, DecodeError
        if protocol_type > 0:
            self.game_log("recv", protocol_type=protocol_type, protocol_instance=protocol_instance)
        return protocol_type, protocol_instance

    def get_pack_length(self):
        """
        :return: 数据包总长度
        """
        try:
            length_bytes = self._sock.recv(4)
        except IOError:
            return -1, IOError
        if length_bytes:
            length = bytes2int(length_bytes)
            return length, "success"
        else:
            return -1, "length cannot be none"

    def get_protocol_type(self):
        """
        :return: 协议号
        """
        try:
            protocol_bytes = self._sock.recv(4)
        except IOError:
            return None
        protocol_type = bytes2int(protocol_bytes)
        return protocol_type

    def send_hello(self):
        self.game_log("info", "say hello")
        data = int2bytes(1)
        self._sock.send(data)

    def receive_hello(self):
        length = self.get_pack_length()[0]
        protocol_type = self.get_protocol_type()
        try:
            res = self._sock.recv(length - 8)
        except ValueError:
            return -1, ValueError
        protocol_instance = protocol_manager.get_protocol_instance(100)
        protocol_instance.ParseFromString(res)
        self.game_log("recv", protocol_type=protocol_type, protocol_instance=protocol_instance)
        return protocol_type, protocol_instance

    def close(self):
        self._sock.close()
