# -- coding: utf-8 --

from flask_restful import Resource, reqparse
from flask import Flask, request, jsonify
import requests
from database import Database
from module import Module

class Hooking(Resource):
    def post(self):
        TAG = "Hooking:"
        module = Module()
        onechat_uri = "https://chat-api.one.th"
        onechat_url1 = onechat_uri + '/message/api/v1/push_quickreply'
        web_vue_url1 = "https://web-meeting-room.herokuapp.com/"
        data = request.json
        onechat_dev_token = "Bearer Af58c5450f3b45c71a97bc51c05373ecefabc49bd2cd94f3c88d5b844813e69a17e26a828c2b64ef889ef0c10e2aee347"
        qr_code_api = "https://api.qrserver.com/v1/create-qr-code/"

        print(TAG, data)
        if(data['event'] == "message"):
            bot_id = data['bot_id']
            user_id = data['source']['user_id']
            email = data['source']['email']
            print(TAG, "bot_id=", bot_id)
            print(TAG, "user_id=", user_id)
            if('data' in data['message']):
                if(data['message']['data'] == "access_req"):
                    print(TAG, "access req recv")

                    cmd = """SELECT bookings.booking_number FROM bookings 
                    WHERE (bookings.meeting_end > (CURRENT_TIMESTAMP)) AND (bookings.one_email = "%s") 
                    ORDER BY bookings.meeting_start
                    LIMIT 1""" %(email)

                    database = Database()
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
                        return module.wrongAPImsg()

                    booking_number = res[0]['result'][0]['booking_number']

                    qr_code_api = qr_code_api + """?data={"booking_number":%s,"one_id":"%s"}""" %(booking_number, email)
                    print(TAG, "qr code generating...")
                    result = requests.get(qr_code_api)
                    if(result.status_code == 200):
                        file_dir = "./"
                        file_name = "tmp_qr.png"
                        print(TAG, "complete")
                        with open(file_dir + file_name, 'wb') as f:
                            f.write(result.content)
                        payload = {"to": user_id, "bot_id": bot_id, "type": "file"}
                        headers = {"Authorization": onechat_dev_token}
                        files = [
                            ('file', (file_name, open(
                                file_dir + file_name,
                                'rb'), 'image/png'))
                        ]
                        r = requests.post(onechat_uri + "/message/api/v1/push_message", files=files, data=payload, headers=headers)
                        print(TAG, r.text)
                        payload = {
                            "to": user_id,
                            "bot_id": bot_id,
                            "type": "text",
                            "message": "แสดง QR Code นี้เพื่อเปิดประตูของคุณเมื่อถึงเวลา",
                            "custom_notification": "เปิดอ่านข้อความใหม่จากทางเรา"
                        }
                        r = requests
            else:
                print(TAG, "menu sending")
                req_body = {
                    "to": user_id,
                    "bot_id": bot_id,
                    "message": "โปรเลือกบริการ",
                    "quick_reply":
                        [{
                            "label": "ระบบจัดการห้องประชุม",
                            "type": "webview",
                            "url": web_vue_url1,
                            "size": "tall",
                            "sign": "false",
                            "onechat_token": "true"
                        },
                        {
                            "label": "แสดง QR Code",
                            "type": "text",
                            "message": "ฉันต้องแสดง QR Code เพื่อเข้าห้องประชุม",
                            "payload": "access_req"
                        }
                        ]
                }

                headers = {"Authorization": onechat_dev_token, "Content-Type": "application/json"}
                result = requests.post(onechat_url1, json=req_body, headers=headers)
                print(TAG, result.text)
        else:
            print(TAG, "unkown data")

        return {
            "type": True,
            "message": "success",
            "elapsed_time_ms": 0,
            "len": 0,
            "result": "testing"
        }
