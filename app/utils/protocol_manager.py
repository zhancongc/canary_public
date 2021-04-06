# coding=utf-8
"""
filename: protocol_manager.py
author: zhancongc@icloud.com
description: protobuf对象池，根据protocol_dict.py的记录，从protocol_xxx_pb2.py中动态引入protobuf对象生成对象实例，复用对象实例
"""

import importlib


class ProtocolManager(object):
    protocol_instance_pool = dict()

    def get_protocol_instance(self, protocol_type):
        """
        :param protocol_type:
        :return: protocol_object
        """
        pro = self.protocol_instance_pool.get(str(protocol_type))
        if pro is None:
            from app.utils import protocol_dict
            pro = protocol_dict.protocol_dict.get(str(protocol_type))
            if pro is None:
                return None
            else:
                self.__add_instance(pro)
                self.protocol_instance_pool.update({
                    str(protocol_type): pro
                })
        if pro.get("instance") is None:
            self.__add_instance(pro)
        return pro.get("instance")

    @staticmethod
    def __add_instance(pro):
        """
        :param pro:
        """
        file_name = pro.get("file_name")
        protocol_name = pro.get("protocol_name")
        module = importlib.import_module(file_name)
        protocol = module.__dict__.get(protocol_name)
        pro.update({"instance": protocol()})


protocol_manager = ProtocolManager()

