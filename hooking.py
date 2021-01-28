from flask_restful import Resource, reqparse
from flask import Flask, request, jsonify
import requests
# -- coding: utf-8 --

class Hooking(Resource):
    def post(self):
        TAG = "Hooking:"
        onechat_url1 = 'https://chat-api.one.th/message/api/v1/push_quickreply'
        web_vue_url1 = "https://web-meeting-room.herokuapp.com/"
        data = request.json
        onechat_dev_token = "Bearer Af58c5450f3b45c71a97bc51c05373ecefabc49bd2cd94f3c88d5b844813e69a17e26a828c2b64ef889ef0c10e2aee347"
        print(TAG, data)
        if(data['event'] == "message"):
            bot_id = data['bot_id']
            user_id = data['source']['user_id']
            print(TAG, "bot_id=", bot_id)
            print(TAG, "user_id=", user_id)

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
                    }]
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
