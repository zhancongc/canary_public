# coding=utf-8
"""
filename: create_superior_account.py
author: zhancongc@icloud.com
description: 创建高级号的流程展示
"""

import sys
import time
from all_servers import all_servers
from app.utils.game_master import GameMaster
from single_client import Robot

try:
    server_id = 19
    login_name = "fly150"
except IndexError as e:
    print(e)
    sys.exit(1)
gm = GameMaster(all_servers.get(server_id))
for i in range(100, 200):
    login_name = "fly" + str(i)
    robot = Robot(7, login_name)
    robot.start()
    robot.stop()
    # role_id = gm.query_base_info_by_login_name(login_name)
    # gm.superior_account(role_id)
gm.close()
