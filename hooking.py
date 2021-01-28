from flask_restful import Resource, reqparse
from flask import Flask, request, jsonify
import requests
# -- coding: utf-8 --

class Hooking(Resource):
    def post(self):
        TAG = "Hooking:"
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
            booking_number = 1
            email = data['source']['email']
            print(TAG, "bot_id=", bot_id)
            print(TAG, "user_id=", user_id)
            if('data' in data['message']):
                if(data['message']['data'] == "access_req"):
                    print(TAG, "access req recv")
                    qr_code_api = qr_code_api + """?data={"booking_number":%s,"one_id":"%s"}""" %(booking_number, email)
                    print(TAG, "qr code generating...")
                    result = requests.get(qr_code_api)
                    if(result.status_code == 200):
                        file_dir = "./"
                        file_name = "tmp_qr.png"
                        print(TAG, "complete")
                        with open(file_dir + file_name, 'wb') as f:
                            f.write(result.content)
                        with open(file_dir + file_name, 'rb') as f:
                            data = {"to": user_id, "bot_id": bot_id, "type": "file"}
                            header = {"Authorization": onechat_dev_token, "Content-Type": "multipart/form-data"}
                            r = requests.post(onechat_uri + "/message/api/v1/push_message", files={'file': f}, data=data)
                            print(TAG, r.text)
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

                header = {"Authorization": onechat_dev_token, "Content-Type": "application/json"}
                result = requests.post(onechat_url1, json=req_body, headers=header)
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
