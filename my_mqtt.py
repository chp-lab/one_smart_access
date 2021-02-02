import paho.mqtt.client as mqtt
from flask_restful import Resource, reqparse
from flask import request
from database import Database
from module import Module
import requests

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
        client_id = "12d62545-176c-4511-b3dc-61148c8e2a44"
        token = "XxABgB71B2zssFGRcz3BrMZdJsb5G5TQ"
        secret = "~#J0UDsDVyfkBBe$taZVetc3q-i_PL8_"
        broker = "mqtt.netpie.io"
        port = 1883
        keep_alive = 60

        client = mqtt.Client(client_id=client_id)
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.username_pw_set(token, secret)

        client.connect(broker, port, keep_alive)

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        print(TAG, "mqtt start")
        client.publish(self.topic + room_num, "1", qos=2)
        client.loop_start()
        client.loop_stop()

    def post(self, room_num):
        TAG= "my_mqtt:"
        onechat_uri = "https://chat-api.one.th"
        onechat_dev_token = "Bearer Af58c5450f3b45c71a97bc51c05373ecefabc49bd2cd94f3c88d5b844813e69a17e26a828c2b64ef889ef0c10e2aee347"
        headers = {"Authorization": onechat_dev_token, "Content-Type": "application/json"}
        bot_id = "B75900943c6205ce084d1c5e8850d40f9"

        module = Module()
        database = Database()

        auth_key = "Authorization"
        if(auth_key not in request.headers):
            return module.unauthorized()

        auth = request.headers.get("Authorization");
        print(TAG, "auth=", auth)
        payload = {
            "bot_id":bot_id,
            "source":auth
        }

        r = requests.post(onechat_uri + "/manage/api/v1/getprofile", headers=headers, json=payload)
        print(TAG, "response code=", r.status_code)
        print(TAG, r.json())

        json_res = r.json()

        if(json_res['status'] == "fail"):
            return module.unauthorized()


        guest_req_key = "guest_req"
        parser = reqparse.RequestParser()
        parser.add_argument(guest_req_key)

        args = parser.parse_args()

        if (not module.isQueryStr(args, guest_req_key)):
            print(TAG, "bad req")
            return module.wrongAPImsg()

        guest_req = args.get(guest_req_key)

        print(TAG, "guest_req=", guest_req)

        if(guest_req == "False"):
            print(TAG, "owner req recv")
            # check are there any booking
            cmd = """SELECT bookings.booking_number, bookings.meeting_start, bookings.meeting_end, bookings.room_num, bookings.agenda
            FROM bookings 
            WHERE bookings.room_num='%s' AND bookings.one_email='%s' AND bookings.meeting_start < (CURRENT_TIMESTAMP) AND bookings.meeting_end > (CURRENT_TIMESTAMP) 
            AND bookings.eject_at IS NULL
            ORDER BY bookings.meeting_start
            LIMIT 1""" %(room_num, json_res['data']['email'])

            res = database.getData(cmd)
            if(res[1] != 200):
                print(TAG, "server error")
                return module.serveErrMsg()
            if(res[0]["len"] == 0):
                return module.measurementNotFound()

            self.unlock(room_num)
            res[0]["help"] = "unlock success"
            print(TAG, res)
            return res
        else:
            print(TAG, "guest_req recv")
            cmd = """SELECT bookings.booking_number, bookings.meeting_start, bookings.meeting_end, bookings.room_num, bookings.agenda
            FROM bookings
            LEFT JOIN guests ON bookings.booking_number=guests.booking_number
            WHERE bookings.room_num='%s' AND guests.guest_email='%s' AND bookings.meeting_start < (CURRENT_TIMESTAMP) AND bookings.meeting_end > (CURRENT_TIMESTAMP) AND bookings.eject_at IS NULL
            ORDER BY bookings.meeting_start
            LIMIT 1""" %(room_num, json_res['data']['email'])

            res = database.getData(cmd)
            if(res[1] != 200):
                print(TAG, "server error")
                return module.serveErrMsg()
            if(res[0]["len"] == 0):
                return module.measurementNotFound()

            self.unlock(room_num)
            res[0]["help"] = "unlock success"
            print(TAG, res)
            return res

if (__name__ == "__main__"):
    my_mqtt = My_mqtt()