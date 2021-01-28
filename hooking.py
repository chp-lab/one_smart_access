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
        print(TAG, data)
        if(data['event'] == "message"):
            bot_id = data['bot_id']
            user_id = data['source']['user_id']
            req_body = {
	"to": user_id,
	"bot_id": bot_id,
	"message": "โปรดเลือกบริการ",
	"quick_reply": [ {
	"label": "ระบบจองห้องประชุม",
	"type": "webview",
	"url": web_vue_url1,
	"size": "tall",
	"sign": "false",
	"onechat_token": "true"
    }]
}
        result = requests.post(onechat_url1, data=req_body)
        print(TAG, result.text)

        return {
            "type": True,
            "message": "success",
            "elapsed_time_ms": 0,
            "len": 0,
            "result": "testing"
        }
