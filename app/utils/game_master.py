# coding=utf-8
"""
filename: game_master.py
author: zhancongc@icloud.com
description: gm指令的python封装
"""
import json
import requests
from requests.auth import HTTPBasicAuth


class GameMaster(object):
    sess = requests.Session()
    auth = HTTPBasicAuth("wlyadmin", "test001")
    server = dict()
    server_url = ""
    game_master_endpoint = {
        "level_up_building": "{server_url}/rest/admin/build?op=update&accid={role_id}&id={building_id}&level={level}",
        "high_account": "{server_url}/rest/admin/role?op=update&accid={role_id}&res_str={res}",
        # 101%3B1%3B999999999 -> 111%3B1%3B999999999 , 154%3B4%3B99999999, 154%3B51%3B111
        "occupy_city": "{server_url}/rest/admin/role?op=update&accid={role_id}&res_str={res}",
        "compile_time": "{server_url}/rest/admin/params?op=get",
        "query_base_info_by_role_id": "{server_url}/rest/admin/role?op=get&accid={role_id}",
        "full_level": "{server_url}/rest/admin/role?op=full_level&accid={role_id}",
    }
    idip_endpoint = {
        "query_base_info_by_login_name": "{idip_url}/rest/ops/idip?idip_sign=4c0a5f42cd1aab18397ca0f36ee62c50"
    }

    def __init__(self, server_dict):
        self.server.update(server_dict)
        self.server_url = "http://{0}:{1}".format(self.server.get("host"), str(self.server.get("admin_port")))
        self.idip_url = "http://{0}:{1}".format(self.server.get("host"), str(self.server.get("idip_port")))

    def close(self):
        self.sess.close()

    def superior_account(self, role_id):
        url_list = list()
        url_list.append(self.game_master_endpoint.get("level_up_building").format(
            server_url=self.server_url, role_id=role_id, building_id=1, level=99))
        for i in range(101, 112):
            url_list.append(self.game_master_endpoint.get("high_account").format(
                server_url=self.server_url, role_id=role_id, res=str(i)+"%3B1%3B999999999"))
        url_list.append(self.game_master_endpoint.get("high_account").format(
            server_url=self.server_url, role_id=role_id, res="154%3B1%3B999999999"))
        url_list.append(self.game_master_endpoint.get("high_account").format(
            server_url=self.server_url, role_id=role_id, res="154%3B51%3B111"))
        url_list.append(self.game_master_endpoint.get("full_level").format(
            server_url=self.server_url, role_id=role_id
        ))

        for url in url_list:
            print("url: ", url)
            res = self.sess.get(url, auth=self.auth)
            print("response", res.text)

    def occupy_city(self, city_id, crop_id):
        pass

    def get_compile_time(self):
        url = self.game_master_endpoint.get("compile_time").format(server_url=self.server_url)
        res = self.sess.get(url, auth=self.auth)
        return res.text

    def query_base_info_by_role_id(self, role_id):
        url = self.game_master_endpoint.get("query_base_info_by_role_id").format(server_url=self.server_url, role_id=role_id)
        res = self.sess.get(url, auth=self.auth)
        return res.text

    def query_base_info_by_login_name(self, login_name):
        url = self.idip_endpoint.get("query_base_info_by_login_name").format(idip_url=self.idip_url)
        data = '''data_packet={{
            "head":{{"PacketLen":null,"Cmdid":4283,"Seqid":1,"ServiceName":"wly2","SendTime":20200731,
                "Version":9,"Authenticate":"","Result":0,"RetErrMsg":""}},
            "body":{{"AreaId":1,"Partition":2,"PlatId":1,"OpenId":"{login_name}","Source":11,
                "Serial":"M-PAYO-20140414124009-58382166"}}
        }}'''.format(login_name=login_name)
        data = data.encode().decode("Latin-1")
        print(url)
        print(data)
        response = self.sess.post(url=url, data=data)
        print(response.text)
        res = json.loads(response.text)
        return res['data']['body']['UsrRoleList'][0]['RoleId']



"""
from app.utils.game_master import GameMaster
from app.all_servers import all_servers
s = all_servers.get(7)
gm = GameMaster(s)
gm.query_base_info_by_login_name("fly100")
"""