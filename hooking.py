from flask_restful import Resource, reqparse
from flask import Flask, request, jsonify
import requests
# -- coding: utf-8 --

class Hooking(Resource):
    def post(self):
        TAG = "Hooking:"
        url = 'https://chat-api.one.th/message/api/v1/push_quickreply'
        data = request.json
        print(TAG, data)
        if(data['event'] == "message"):
            bot_id = data['bot_id']
            user_id = data['source']['user_id']
            req_body = {
	"to": "U18a33b1dcddf59da8000068357b3c745",
	"bot_id": "B75900943c6205ce084d1c5e8850d40f9",
	"message": "โปรดเลือกบริการ",
	"quick_reply": [ {
	"label": "ระบบจองห้องประชุม",
	"type": "webview",
	"url": "https://web-meeting-room.herokuapp.com/",
	"size": "tall",
	"sign": "false",
	"onechat_token": "true"
    }]
}
        result = requests.post(url, data=req_body)
        print(TAG, result.text)

        return {
            "type": True,
            "message": "success",
            "elapsed_time_ms": 0,
            "len": 0,
            "result": "testing"
        }
