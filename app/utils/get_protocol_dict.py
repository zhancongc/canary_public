# coding=utf-8
"""
filename: get_protocol_dict.py
author: zhancongc@icloud.com
description: 遍历所有的protocol_xxx_pb2.py文件，找到protobuf对象，记录下协议号和文件名
"""

import os
import sys
import json
import importlib
from google.protobuf.descriptor import Descriptor
sys.path.append("..")


def get_protocol_class(file_path):
    protocol_dict = dict()
    for f in os.listdir(file_path):
        if f.split(".")[1] == "py" and f[0] != "_":
            suffix = "protocol_py.{0}".format(f.split(".")[0])
            module = importlib.import_module(suffix)
            for class_name in dir(module):
                if class_name[0] == "_":
                    element = module.__dict__.get(class_name)
                    if type(element) == Descriptor:
                        try:
                            protocol_name = element.name
                            protocol_num = element.fields_by_name["type"].default_value
                            protocol_dict.update({
                                protocol_num: {
                                    "file_name": suffix,
                                    "protocol_name": protocol_name
                                }
                            })
                        except Exception as e:
                            print(class_name, e)

    protocol_dict.update({0: {"file_name": "protocol_py.protocol_base_pb2", "protocol_name": "C2S_SystemTick"}})
    return protocol_dict


with open("utils/protocol_dict.py", "w") as fp:
    fp.write("protocol_dict=" + json.dumps(get_protocol_class("../protocol_py")))

