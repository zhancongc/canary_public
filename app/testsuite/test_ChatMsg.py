# coding=utf-8
"""
filename: test_ChatMsg.py
author: zhancongc@icloud.com
description:
    message C2S_ChatMsg {
        optional ProtocolType type = 1 [default = 7801];
        optional int32 msg_type = 2;
        optional int32 zone_id = 3;
        optional string contact_player_name = 4;
        optional string content = 5;
        optional int32 content_type_num = 6;
        optional int32 content_type = 7;
        optional int64 to_role_id = 8;
    }
    message S2C_ChatMsg {
            optional ProtocolType type = 1 [default = 7802];
            enum ChatType{
                system   = 1;
                sender   = 2;
                accepter = 3;
            }
            optional int32 ret = 2;
            optional ChatMessage msg = 25;
    }
"""


from app.single_client import Robot


class TestChatMsg:
    protocol_type = 7801
    login_name = "fly150"
    server_id = 7
    robot = None

    def setup_method(self, method):
        self.robot = Robot(self.server_id, self.login_name)
        self.robot.start()

    def teardown_method(self, method):
        self.robot.stop()

    def test_ChatMsg_01(self):
        data = {"msg_type": 2, "zone_id": 0, "contact_player_name": "", "content": "Hello, world! 01",
             "content_type_num": 1, "to_role_id": 0}
        self.robot.send(self.protocol_type, data)
        res = self.robot.get_response()
        assert res[1].msg.role_id == int(self.robot.client.role_id)

    def test_ChatMsg_02(self):
        data = {"msg_type": 3, "zone_id": 0, "contact_player_name": "", "content": "Hello, world! 02",
             "content_type_num": 1, "to_role_id": 0}
        self.robot.send(self.protocol_type, data)
        res = self.robot.get_response()
        assert res[1].msg.role_id == int(self.robot.client.role_id)


