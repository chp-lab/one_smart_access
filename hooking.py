# -- coding: utf-8 --

from flask_restful import Resource
from flask import request
import requests
from database import Database
from module import Module

class Hooking(Resource):
    onechat_uri = "https://chat-api.one.th"
    onechat_dev_token = "Bearer Af58c5450f3b45c71a97bc51c05373ecefabc49bd2cd94f3c88d5b844813e69a17e26a828c2b64ef889ef0c10e2aee347"
    onechat_url1 = onechat_uri + '/message/api/v1/push_quickreply'
    def menu_send(self, user_id, bot_id):
        TAG = "menu_send:"
        # web_vue_url1 = "https://web-meeting-room.herokuapp.com/"
        web_vue_url1 = "https://onesmartaccess.herokuapp.com/"
        req_body = {
            "to": user_id,
            "bot_id": bot_id,
            "message": "ท่านต้องการบริการอะไรหรือไม่",
            "quick_reply":
                [
                {
                    "label": "เข้าพื้นที่",
                    "type": "webview",
                    "size": "full",
                    "url": web_vue_url1,
                    "sign": "false",
                    "onechat_token": "true"
                },
                {
                    "label": "จัดการห้อง",
                    "type": "webview",
                    "size": "full",
                    "url": web_vue_url1,
                    "sign": "false",
                    "onechat_token": "true"
                },
                {
                    "label": "การจองของคุณ",
                    "type": "text",
                    "message": "ต้องการดูการจองของฉัน",
                    "payload": "list_all_booking"
                },
                # {
                #     "label": "แสดงกุญแจของคุณ",
                #     "type": "text",
                #     "message": "ฉันต้องแสดง QR Code เพื่อเข้าห้องประชุม",
                #     "payload": "access_req"
                # },
                {
                    "label": "คำเชิญ",
                    "type": "text",
                    "message": "ขอดูคำเชิญ",
                    "payload": "invite"
                }
                # {
                #     "label": "ขอกุญแจที่ถูกเชิญ",
                #     "type": "text",
                #     "message": "ขอ QR Code ที่ถูกเชิญ",
                #     "payload": "guest_req"
                # },
                # {
                #     "label": "OBox",
                #     "type": "webview",
                #     "url": "http://onesmartaccess.ddns.net:9000/examples/simple/",
                #     "size": "full",
                #     "sign": "false",
                #     "onechat_token": "true"
                # },
                # {
                #     "label": "Farm",
                #     "type": "webview",
                #     "url": "https://9eb2bbd4d505.ngrok.io/",
                #     "size": "full",
                #     "sign": "false",
                #     "onechat_token": "true"
                # }
                ]
        }
        headers = {"Authorization": self.onechat_dev_token, "Content-Type": "application/json"}
        result = requests.post(self.onechat_url1, json=req_body, headers=headers)
        print(TAG, result.text)
    def send_msg(self, one_id, reply_msg):
        TAG = "send_msg:"
        bot_id = "B75900943c6205ce084d1c5e8850d40f9"
        headers = {"Authorization": self.onechat_dev_token, "Content-Type": "application/json"}
        payload = {
            "to": one_id,
            "bot_id": bot_id,
            "type": "text",
            "message": reply_msg,
            "custom_notification": "เปิดอ่านข้อความใหม่จากทางเรา"
        }
        r = requests.post(self.onechat_uri + "/message/api/v1/push_message", headers=headers, json=payload)
        # self.menu_send(one_id, bot_id)
        return r

    def is_user_exist(self, one_email):
        TAG = "is_user_exist:"
        cmd = """SELECT users.one_email FROM users WHERE users.one_email='%s' """ %(one_email)
        database = Database()
        res = database.getData(cmd)
        print(TAG, "res=", res)
        if(res[0]['len'] > 0):
            return True
        else:
            return False

    def add_new_user(self, email, name, one_id):
        TAG = "add_new_user:"
        database = Database()
        print(TAG, "add user to our system")
        sql = """INSERT INTO `users` (`one_email`, `name`, `one_id`) VALUES ('%s', '%s', '%s')""" \
              % (email, name, one_id)
        insert = database.insertData(sql)
        return insert

    def post(self):
        TAG = "Hooking:"
        database = Database()
        module = Module()
        onechat_uri = self.onechat_uri
        data = request.json
        onechat_dev_token = "Bearer Af58c5450f3b45c71a97bc51c05373ecefabc49bd2cd94f3c88d5b844813e69a17e26a828c2b64ef889ef0c10e2aee347"
        qr_code_api = "https://api.qrserver.com/v1/create-qr-code/"
        headers = {"Authorization": onechat_dev_token}

        print(TAG, "data=", data)
        print(TAG, request.headers)
        if(data['event'] == "message"):
            bot_id = data['bot_id']
            user_id = data['source']['user_id']
            email = data['source']['email']
            one_id = data['source']['one_id']
            name = data['source']['display_name']
            user_exist = self.is_user_exist(email)
            # real is user_exist
            # edit line bellow
            if(user_exist):
                print(TAG, "user exist!")
            else:
                print(TAG, "usr not exist!")
                # check that is req from INET employee
                # covid_tk_uri = "https://api.covid19.inet.co.th/api/v1/health/"
                # cv_token = "Bearer Q27ldU/si5gO/h5+OtbwlN5Ti8bDUdjHeapuXGJFoUP+mA0/VJ9z83cF8O+MKNcBS3wp/pNxUWUf5GrBQpjTGq/aWVugF0Yr/72fwPSTALCVfuRDir90sVl2bNx/ZUuAfA=="
                # cv = requests.get(covid_tk_uri + one_id, headers={"Authorization": cv_token})
                # print(TAG, "cv=", cv.json())
                # cv_json = cv.json()
                # print(TAG, "cv_json=", cv_json)
                #
                # if (cv_json["msg"] == "forbidden"):
                #     print(TAG, "user not in our company")
                #     # send message via bot to reject user
                #     # api return
                # else:
                #     # add user to database
                #     # process continue
                # print(TAG, "add user to our system")
                # sql = """INSERT INTO `users` (`one_email`, `name`, `one_id`) VALUES ('%s', '%s', '%s')""" \
                #       % (email, name, one_id)
                # insert = database.insertData(sql)
                # print(TAG, "insert=", insert)
                add_user = self.add_new_user(email, name, one_id)
                print(TAG, "add=new_user=", add_user)

            print(TAG, "bot_id=", bot_id)
            print(TAG, "user_id=", user_id)
            if('data' in data['message']):
                if(data['message']['data'] == "access_req"):
                    print(TAG, "access req recv")

                    cmd = """SELECT bookings.booking_number, bookings.room_num, bookings.agenda,
                    bookings.meeting_start, bookings.meeting_end FROM bookings 
                    WHERE (bookings.meeting_end > (CURRENT_TIMESTAMP)) AND (bookings.one_email = "%s") 
                    ORDER BY bookings.meeting_start
                    LIMIT 1""" %(email)

                    res = database.getData(cmd)

                    print(TAG, "res=", res)

                    if(res[0]['len'] == 0):
                        payload = {
                            "to": user_id,
                            "bot_id": bot_id,
                            "type": "text",
                            "message": "ไม่พบข้อมูลการจองของคุณ",
                            "custom_notification": "เปิดอ่านข้อความใหม่จากทางเรา"
                        }
                        headers = {"Authorization": onechat_dev_token, "Content-Type": "application/json"}
                        r = requests.post(onechat_uri + "/message/api/v1/push_message", json=payload, headers=headers)
                        print(TAG, r.text)
                        self.menu_send(user_id, bot_id)
                        return module.wrongAPImsg()

                    booking_number = res[0]['result'][0]['booking_number']
                    booking_data = res[0]['result'][0]

                    qr_code_api = qr_code_api + """?data={"booking_number":%s,"one_id":"%s"}&size=300x300""" %(booking_number, email)
                    print(TAG, "qr code generating...")
                    result = requests.get(qr_code_api)
                    if(result.status_code == 200):
                        file_dir = "./"
                        file_name = "tmp_qr.png"
                        print(TAG, "complete")
                        with open(file_dir + file_name, 'wb') as f:
                            f.write(result.content)
                        payload = {"to": user_id, "bot_id": bot_id, "type": "file"}

                        files = [
                            ('file', (file_name, open(
                                file_dir + file_name,
                                'rb'), 'image/png'))
                        ]
                        r = requests.post(onechat_uri + "/message/api/v1/push_message", files=files, data=payload, headers=headers)
                        print(TAG, r.text)
                        reply_msg = """ห้อง %s เหตุผล %s เวลาเริ่ม %s เวลาสิ้นสุด %s แสกน QR Code หน้าห้องเมื่อถึงเวลา""" \
                                    %(booking_data['room_num'], booking_data['agenda'], booking_data['meeting_start'], booking_data['meeting_end'])
                        payload = {
                            "to": user_id,
                            "bot_id": bot_id,
                            "type": "text",
                            "message": reply_msg,
                            "custom_notification": "เปิดอ่านข้อความใหม่จากทางเรา"
                        }
                        r = requests.post(onechat_uri + "/message/api/v1/push_message", headers=headers, json=payload)
                        self.menu_send(user_id, bot_id)
                        print(TAG, r.text)
                elif(data['message']['data'] == "list_all_booking"):
                    print(TAG, "list all access")
                    cmd = """SELECT bookings.booking_number, bookings.room_num, bookings.agenda, bookings.meeting_start, bookings.meeting_end 
                    FROM bookings 
                    WHERE bookings.one_email='%s' AND bookings.meeting_end > (CURRENT_TIMESTAMP) AND bookings.eject_at IS NULL
                    ORDER BY bookings.meeting_start""" %(email)
                    res = database.getData(cmd)
                    print(TAG, "res=", res)
                    if (res[1] == 200):
                        reply_msg = """คุณมี %s การจอง """ %(res[0]['len'])
                        booking_list = res[0]['result']
                        for i in range(res[0]['len']):
                            print(TAG, "booking:", booking_list[i])
                            tmp_list = booking_list[i]
                            reply_msg = reply_msg + """%s.ห้อง %s เลขที่การจอง %s เหตุผล %s เวลาเริ่มต้น %s เวลาสิ้นสุด %s\n""" \
                                           %(i + 1, tmp_list['room_num'], tmp_list['booking_number'], tmp_list['agenda'],
                                             tmp_list['meeting_start'], tmp_list['meeting_end'])

                        payload = {
                            "to": user_id,
                            "bot_id": bot_id,
                            "type": "text",
                            "message": reply_msg,
                            "custom_notification": "เปิดอ่านข้อความใหม่จากทางเรา"
                        }
                        r = requests.post(onechat_uri + "/message/api/v1/push_message", headers=headers, json=payload)
                        print(TAG, r.text)
                        self.menu_send(user_id, bot_id)
                elif (data['message']['data'] == "invite"):
                    print(TAG, "list all valid invite")
                    cmd = """SELECT bookings.booking_number, bookings.room_num, bookings.agenda, bookings.meeting_start, bookings.meeting_end FROM bookings
                    LEFT JOIN guests ON bookings.booking_number = guests.booking_number
                    WHERE guests.guest_email='%s' AND bookings.meeting_end > (CURRENT_TIMESTAMP) AND bookings.eject_at IS NULL""" %(email)

                    res = database.getData(cmd)
                    print(TAG, "res=", res)
                    if (res[1] == 200):
                        reply_msg = """คุณมี %s คำเชิญ """ % (res[0]['len'])
                        booking_list = res[0]['result']
                        for i in range(res[0]['len']):
                            print(TAG, "booking:", booking_list[i])
                            tmp_list = booking_list[i]
                            reply_msg = reply_msg + """%s.ห้อง %s เลขที่การจอง %s เหตุผล %s เวลาเริ่มต้น %s เวลาสิ้นสุด %s\n""" \
                                        % (i + 1, tmp_list['room_num'], tmp_list['booking_number'], tmp_list['agenda'],
                                           tmp_list['meeting_start'], tmp_list['meeting_end'])

                        payload = {
                            "to": user_id,
                            "bot_id": bot_id,
                            "type": "text",
                            "message": reply_msg,
                            "custom_notification": "เปิดอ่านข้อความใหม่จากทางเรา"
                        }
                        r = requests.post(onechat_uri + "/message/api/v1/push_message", headers=headers, json=payload)
                        print(TAG, r.text)
                        self.menu_send(user_id, bot_id)
                elif (data['message']['data'] == "guest_req"):
                    print(TAG, "guest req recv")

                    cmd = """SELECT bookings.booking_number, bookings.room_num, bookings.agenda, bookings.meeting_start, bookings.meeting_end 
                    FROM `bookings` 
                    LEFT JOIN guests ON bookings.booking_number=guests.booking_number
                    WHERE (bookings.meeting_end > (CURRENT_TIMESTAMP)) AND (guests.guest_email = "%s")
                    ORDER BY bookings.meeting_start LIMIT 1""" % (email)

                    res = database.getData(cmd)

                    print(TAG, "res=", res)

                    if (res[0]['len'] == 0):
                        payload = {
                            "to": user_id,
                            "bot_id": bot_id,
                            "type": "text",
                            "message": "ไม่พบข้อมูลคำเชิญที่คุณได้รับ",
                            "custom_notification": "เปิดอ่านข้อความใหม่จากทางเรา"
                        }
                        headers = {"Authorization": onechat_dev_token, "Content-Type": "application/json"}
                        r = requests.post(onechat_uri + "/message/api/v1/push_message", json=payload, headers=headers)
                        print(TAG, r.text)
                        self.menu_send(user_id, bot_id)
                        return module.wrongAPImsg()

                    booking_number = res[0]['result'][0]['booking_number']
                    booking_data = res[0]['result'][0]

                    qr_code_api = qr_code_api + """?data={"booking_number":%s,"one_id":"%s","guest_req":%s}&size=300x300""" % (
                    booking_number, email, 1)
                    print(TAG, "qr code generating...")
                    result = requests.get(qr_code_api)
                    if (result.status_code == 200):
                        file_dir = "./"
                        file_name = "tmp_qr.png"
                        print(TAG, "complete")
                        with open(file_dir + file_name, 'wb') as f:
                            f.write(result.content)
                        payload = {"to": user_id, "bot_id": bot_id, "type": "file"}

                        files = [
                            ('file', (file_name, open(
                                file_dir + file_name,
                                'rb'), 'image/png'))
                        ]
                        r = requests.post(onechat_uri + "/message/api/v1/push_message", files=files, data=payload,
                                          headers=headers)
                        print(TAG, r.text)
                        reply_msg = """ห้อง %s เหตุผล %s เวลาเริ่ม %s เวลาสิ้นสุด %s แสกน QR Code หน้าห้องเมื่อถึงเวลา""" \
                                    % (booking_data['room_num'], booking_data['agenda'], booking_data['meeting_start'],
                                       booking_data['meeting_end'])
                        payload = {
                            "to": user_id,
                            "bot_id": bot_id,
                            "type": "text",
                            "message": reply_msg,
                            "custom_notification": "เปิดอ่านข้อความใหม่จากทางเรา"
                        }
                        r = requests.post(onechat_uri + "/message/api/v1/push_message", headers=headers, json=payload)
                        self.menu_send(user_id, bot_id)
                        print(TAG, r.text)
                # elif("booking_req" in data['message']['data']):
                #     print(TAG, "booking req recv")
                #     headers = {"Authorization": onechat_dev_token, "Content-Type": "application/json"}
                #     booking_sate = data["message"]["data"]["booking_state"]
                #     reply_msg = "เริ่มต้นการจอง"
                #
                #     meeting_start = None
                #     meeting_end = None
                #     room_num = None
                #     agenda = None
                #
                #     if(booking_sate == "start"):
                #         print(TAG, "เริ่มต้นการจอง")
                #         reply_msg = "กรุณาระบุเวลาเริ่มต้น (ตัวอย่าง 14:15 หรือ 8:30)"
                #     payload = {
                #         "to": user_id,
                #         "bot_id": bot_id,
                #         "type": "text",
                #         "message": reply_msg,
                #         "custom_notification": "เปิดอ่านข้อความใหม่จากทางเรา"
                #     }
                #     r = requests.post(onechat_uri + "/message/api/v1/push_message", headers=headers, json=payload)
                #     print(r.text)
                else:
                    print(TAG, "Unknow service")
            else:
                self.menu_send(user_id, bot_id)
                print(TAG, "menu sending")
        elif(data['event'] == "add_friend"):
            bot_id = data['bot_id']
            user_id = data['source']['user_id']
            email = data['source']['email']
        else:
            print(TAG, "unkown data")

        return {
            "type": True,
            "message": "success",
            "elapsed_time_ms": 0,
            "len": 0,
            "result": "testing"
        }
