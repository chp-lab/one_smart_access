import paho.mqtt.client as mqtt
from flask_restful import Resource, reqparse
from flask import request
from database import Database
from module import Module
import requests
from hooking import Hooking

class My_mqtt(Resource):
    topic = "@msg/set/status/"

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        # client.subscribe(self.topic)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))

    def unlock(self, room_num):
        TAG = "my_mqttinit:"
        # client_id = "12d62545-176c-4511-b3dc-61148c8e2a44"
        # token = "XxABgB71B2zssFGRcz3BrMZdJsb5G5TQ"
        # secret = "~#J0UDsDVyfkBBe$taZVetc3q-i_PL8_"
        # broker = "mqtt.netpie.io"
        port = 1883
        keep_alive = 60

        broker = "localhost"
        token = "chp-lab"
        secret = "atop3352"

        # client = mqtt.Client(client_id=client_id)
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.username_pw_set(token, secret)

        client.connect(broker, port, keep_alive)

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        print(TAG, "mqtt start")
        print(TAG, "publish topic:" + self.topic + room_num, "payload:", "1")
        client.publish(self.topic + room_num, "1", qos=2)
        client.loop_start()
        print(TAG, "client stop")
        client.loop_stop()

    def post(self, room_num):
        TAG= "my_mqtt:"
        my_hooking = Hooking()
        onechat_uri = "https://chat-api.one.th"
        onechat_dev_token = "Bearer Af58c5450f3b45c71a97bc51c05373ecefabc49bd2cd94f3c88d5b844813e69a17e26a828c2b64ef889ef0c10e2aee347"
        headers = {"Authorization": onechat_dev_token, "Content-Type": "application/json"}
        bot_id = "B75900943c6205ce084d1c5e8850d40f9"

        module = Module()
        database = Database()

        auth_key = "Authorization"
        if(auth_key not in request.headers):
            return module.unauthorized()

        auth = request.headers.get("Authorization")
        print(TAG, "auth=", auth)
        payload = {
            "bot_id":bot_id,
            "source":auth
        }

        r = requests.post(onechat_uri + "/manage/api/v1/getprofile", headers=headers, json=payload)
        print(TAG, "response code=", r.status_code)
        # print(TAG, r.json())

        json_res = r.json()
        print(TAG, "json_res=", json_res)

        if(json_res['status'] == "fail"):
            print(TAG, "not found in one platform")
            # my_hooking.send_msg(one_id, "คุณไม่มีสิทธ์เข้าถึงระบบ")
            return module.unauthorized()

        one_id = json_res['data']['one_id']
        print(TAG, "process the req")

        guest_req_key = "guest_req"
        parser = reqparse.RequestParser()
        parser.add_argument(guest_req_key)

        args = parser.parse_args()

        if (not module.isQueryStr(args, guest_req_key)):
            print(TAG, "bad api calling")
            return module.wrongAPImsg()

        guest_req = args.get(guest_req_key)
        print(TAG, "guest_req=", guest_req)
        one_email = json_res['data']['email']
        name = json_res['data']['nickname']

        userExist = my_hooking.is_user_exist(one_email)

        if(not userExist):
            print(TAG, "add new user to the system")
            my_hooking.add_new_user(one_email, name, one_id)

        if(guest_req == "no"):
            print(TAG, "owner req recv")
            # one_email = json_res['data']['email']
            # check are there any booking
            cmd = """SELECT bookings.booking_number, bookings.meeting_start, bookings.meeting_end, bookings.room_num, bookings.agenda
            FROM bookings 
            WHERE bookings.room_num='%s' AND bookings.one_email='%s' AND bookings.meeting_start < (CURRENT_TIMESTAMP) AND bookings.meeting_end > (CURRENT_TIMESTAMP) 
            AND bookings.eject_at IS NULL
            ORDER BY bookings.meeting_start
            LIMIT 1""" %(room_num, one_email)

            res = database.getData(cmd)
            # print(TAG, "res=", res)
            if(res[1] != 200):
                print(TAG, "server error")
                return module.serveErrMsg()
            if(res[0]["len"] == 0):
                my_hooking.send_msg(one_id, "ไม่พบการจองห้อง %s ของคุณเวลานี้" % (room_num))
                return module.measurementNotFound()

            meeting_start = res[0]['result'][0]['meeting_start']
            meeting_end = res[0]['result'][0]['meeting_end']
            booking_number = res[0]['result'][0]['booking_number']

            print(TAG, "unlock room_num=", room_num)
            self.unlock(room_num)
            res[0]["help"] = "unlock success"
            print(TAG, res)

            sql = """INSERT INTO access_logs (booking_number, one_email) VALUES (%s, '%s')""" %(booking_number, one_email)
            insert = database.insertData(sql)
            print(TAG, "insert=", insert)

            my_hooking.send_msg(one_id, "ขอต้อนรับสู่ห้อง %s เริ่มประชุม %s ถึง %s" % (room_num, meeting_start, meeting_end))

            return res
        elif(guest_req == "none"):
            print(TAG, "main door req recv")
            cmd = """SELECT rooms.building, (CURRENT_TIMESTAMP) as cur_time FROM rooms WHERE rooms.room_num='%s' AND rooms.main_door=1""" % (room_num)
            res = database.getData(cmd)
            print(TAG, "res=", res)
            if (res[0]['len'] == 0):
                print(TAG, "bad req")
                return module.wrongAPImsg()

            # one_email = json_res["data"]["email"]
            one_id = json_res['data']['one_id']
            print(TAG, "res=", res)
            cur_time = res[0]["result"][0]["cur_time"]
            building = res[0]["result"][0]["building"]

            print(TAG, "one_email=", one_email)
            print(TAG, "cur_time=", cur_time)

            # call covid tracking api
            covid_tk_uri = "https://api.covid19.inet.co.th/api/v1/health/"
            cv_token = "Bearer Q27ldU/si5gO/h5+OtbwlN5Ti8bDUdjHeapuXGJFoUP+mA0/VJ9z83cF8O+MKNcBS3wp/pNxUWUf5GrBQpjTGq/aWVugF0Yr/72fwPSTALCVfuRDir90sVl2bNx/ZUuAfA=="
            cv = requests.get(covid_tk_uri + one_id, headers={"Authorization": cv_token})
            print(TAG, "cv=", cv.json())
            cv_json = cv.json()
            if (cv_json["msg"] != "success"):
                return {
                    "type": False,
                    "message": "fail",
                    "error_message": "Unauthorized",
                    "result": None,
                    "help": "Main door.User may not found in covid tracking, please add covid tracking bot as new friend and give access permission"
                }
            # check access permission from covid lv.
            # then reture result to client
            door_action = "open"
            msg = ""
            help = "หมั่นล้างมือ ใส่หน้ากากอนามัยและรักษาระยะห่างจากผู้อื่น"
            covid_lv = cv_json["data"]
            # covid_lv = "orange"
            # covid_lv_th = None

            if (covid_lv == ""):
                door_action = "not_open"
                door_action_th = "ปิด"
                msg = "data_not_found"
                help = """• สถานะประตู %s\r\n• %s น. \r\n• สถานที่ %s\r\n• คำแนะนำ กรุณาประเมินความเสี่ยง Covid-19 ก่อนเข้าพื้นที่ค่ะ""" %(door_action_th, cur_time, building)
                # covid_lv_th = "ยังไม่ทำแบบประเมินความเสี่ยง"
            elif (covid_lv == "green"):
                msg = "normal"
                covid_lv_th = "เขียว"
                door_action_th = "เปิด"
                help = """• สถานะประตู %s\r\n• วันเวลา %s น.\r\n• สถานที่ %s\r\n• สถานะความเสี่ยงโควิดของคุณคือ %s""" % (door_action_th, cur_time, building, covid_lv_th)
            elif (covid_lv == "yellow"):
                msg = "ok"
                covid_lv_th = "เหลือง"
                door_action_th = "เปิด"
                help = """• สถานะประตู %s\r\n• วันเวลา %s น.\r\n• สถานที่ %s\r\n• สถานะความเสี่ยงโควิดของคุณคือ %s""" % (door_action_th, cur_time, building, covid_lv_th)
            elif (covid_lv == "orange"):
                door_action = "not_open"
                msg = "warning"
                covid_lv_th = "ส้ม"
                door_action_th = "ปิด"
                help = """• สถานะประตู %s\r\n• วันเวลา %s น.\r\n• สถานที่ %s\r\n• สถานะความเสี่ยงโควิดของคุณคือ %s""" % (door_action_th, cur_time, building, covid_lv_th)
            elif (covid_lv == "red"):
                door_action = "not_open"
                msg = "danger"
                covid_lv_th = "แดง"
                door_action_th = "ปิด"
                help = """• สถานะประตู %s\r\n• วันเวลา %s น.\r\n• สถานที่ %s\r\n• สถานะความเสี่ยงโควิดของคุณคือ %s""" % (door_action_th, cur_time, building, covid_lv_th)
            else:
                door_action = "not_open"
                msg = "unkonw"
                covid_lv_th = "ไม่ทราบสถานะ"
                help = "ไม่ทราบสถานะ กรุณาติดต่อเจ้าหน้าที่เพื่อขอเข้าพื้นที่"

            if (door_action == "open"):
                self.unlock(room_num)

            sql = """INSERT INTO covid_tracking_log (room_num, covid_level, door_action, one_email, one_id)
            VALUES ('%s', '%s', '%s', '%s', %s)""" %(room_num, covid_lv, door_action, one_email, one_id)

            # my_msg = None
            # if(door_action == "open"):
            #     my_msg = "เปิดประตูสำเร็จ "
            # else:
            #     my_msg = "ห้ามเข้าพื้นที่"
            # insert data
            insert = database.insertData(sql)

            r = my_hooking.send_msg(one_id, help);
            print(TAG, r.text)

            print(TAG, "insert=", insert)

            result = {
                "type": True,
                "message": "success",
                "error_message": None,
                "result": [
                    {
                        "covid_level": covid_lv,
                        "door_action": door_action,
                        "msg": msg
                    }
                ],
                "help": help
            }
            return result
        elif(guest_req == "yes"):
            print(TAG, "guest_req recv")
            # one_email = json_res['data']['email']

            cmd = """SELECT bookings.booking_number, bookings.meeting_start, bookings.meeting_end, bookings.room_num, bookings.agenda
            FROM bookings
            LEFT JOIN guests ON bookings.booking_number=guests.booking_number
            WHERE bookings.room_num='%s' AND guests.guest_email='%s' AND bookings.meeting_start < (CURRENT_TIMESTAMP) AND bookings.meeting_end > (CURRENT_TIMESTAMP) AND bookings.eject_at IS NULL
            ORDER BY bookings.meeting_start
            LIMIT 1""" %(room_num, one_email)

            res = database.getData(cmd)
            print(TAG, "cmd=", cmd)
            print(TAG, "res=", res)

            if(res[1] != 200):
                print(TAG, "server error")
                return module.serveErrMsg()
            if(res[0]["len"] == 0):
                my_hooking.send_msg(one_id, "ไม่พบคำเชิญเข้าห้อง %s ของคุณเวลานี้")
                return module.measurementNotFound()

            self.unlock(room_num)
            res[0]["help"] = "unlock success"
            print(TAG, res)

            booking_number = res[0]['result'][0]['booking_number']
            meeting_start = res[0]['result'][0]['meeting_start']
            meeting_end = res[0]['result'][0]['meeting_end']
            my_hooking.send_msg(one_id, "ขอต้อนรับสู่ห้อง %s เริ่มประชุม %s ถึง %s" %(room_num, meeting_start, meeting_end))

            sql = """INSERT INTO access_logs (booking_number, one_email) VALUES (%s, '%s')""" % (
            booking_number, one_email)

            insert = database.insertData(sql)
            print(TAG, "insert=", insert)

            return res
        elif(guest_req == "admin"):
            print(TAG, "admin req recv")
            cmd = """SELECT users.name FROM users WHERE users.one_email='%s' AND users.role='admin'""" %(one_email)
            res = database.getData(cmd)
            print(TAG, "res=", res)
            if(res[0]['len'] == 0):
                return module.unauthorized()
            self.unlock(room_num)
            res = {
                "type": True,
                "message": "success",
                "error_message": None,
                "len": 1,
                "result": [
                    {
                        "booking_number": 0,
                        "meeting_start": "- -",
                        "meeting_end": "- -",
                        "room_num": room_num,
                        "agenda": "สิทธิ์แอดมิน",
                        "help": "unlock success"
                    }
                ]
            }
            return res
        elif (guest_req == "checkin"):
            print(TAG, "checkin req recv")
            cmd = """SELECT users.name, users.one_email, users.one_id FROM users WHERE users.one_email='%s'""" % (one_email)
            res = database.getData(cmd)

            print(TAG, "res=", res)
            if (res[0]['len'] == 0):
                return module.unauthorized()
            user_data = res[0]['result'][0]

            cmd = """SELECT rooms.building, (CURRENT_TIMESTAMP) as cur_time FROM rooms WHERE rooms.room_num='%s' AND rooms.main_door=1""" % (room_num)
            res = database.getData(cmd)
            print(TAG, "res=", res)
            if (res[0]['len'] == 0):
                print(TAG, "bad req")
                return module.unauthorized()

            self.unlock(room_num)
            res = {
                "type": True,
                "message": "success",
                "error_message": None,
                "len": 1,
                "result": [
                    {
                        "door":"open_success",
                        "one_email":user_data['one_email'],
                        "one_id":user_data['one_id'],
                        "nickname":user_data['name']
                    }
                ]
            }
            return res
        else:
            return module.wrongAPImsg()


if (__name__ == "__main__"):
    my_mqtt = My_mqtt()