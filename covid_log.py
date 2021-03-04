from flask_restful import Resource
from flask import request
from database import Database
from module import Module
import requests

class Covid_log(Resource):
    def get_user_data(self, auth):
        TAG = "get_user_data:"
        TAG = "covid_log:"

        onechat_uri = "https://chat-api.one.th"
        onechat_dev_token = "Bearer Af58c5450f3b45c71a97bc51c05373ecefabc49bd2cd94f3c88d5b844813e69a17e26a828c2b64ef889ef0c10e2aee347"
        headers = {"Authorization": onechat_dev_token, "Content-Type": "application/json"}
        bot_id = "B75900943c6205ce084d1c5e8850d40f9"

        payload = {
            "bot_id":bot_id,
            "source":auth
        }

        r = requests.post(onechat_uri + "/manage/api/v1/getprofile", headers=headers, json=payload)
        print(TAG, "response code=", r.status_code)
        json_res = r.json()
        return json_res

    def get(self):
        TAG = "covid_log:"
        module = Module()
        database = Database()

        auth_key = "Authorization"
        if(auth_key not in request.headers):
            return module.unauthorized()
        auth = request.headers.get("Authorization")
        print(TAG, "auth=", auth)

        json_res = self.get_user_data(auth)
        print(TAG, "json_res=", json_res)
        return "developing"



