import paho.mqtt.client as mqtt
from flask_restful import Resource, reqparse
from database import Database
from module import Module

class My_mqtt(Resource):
    topic = "@msg/set/status/5-0_OAI"

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        # client.subscribe(self.topic)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))

    def __init__(self):
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
        client.publish(self.topic, "1")
        client.loop_start()
        # while True:
        #     TAG  = "test"

    def post(self, room_num):
        TAG= "my_mqtt:"

        module = Module()
        database = Database()

        guest_req_key = "guest_req"
        parser = reqparse.RequestParser()
        parser.add_argument(guest_req_key)

        args = parser.parse_args()

        if (not module.isQueryStr(args, guest_req_key)):
            print(TAG, "bad req")
            return module.wrongAPImsg()

        guest_req = args.get(guest_req_key)

        if(not guest_req):
            cmd = """SELECT bookings.booking_number, bookings.meeting_start, bookings.meeting_end
            FROM bookings 
            WHERE bookings.room_num='%s' AND bookings.one_email='chatpeth.ke@one.th' AND bookings.meeting_start < (CURRENT_TIMESTAMP) AND bookings.meeting_end > (CURRENT_TIMESTAMP)
            ORDER BY bookings.meeting_start
            LIMIT 1""" %(room_num)

            res = database.getData(cmd)

            print(TAG, res)
            return res
        else:
            return "developing"

if (__name__ == "__main__"):
    my_mqtt = My_mqtt()