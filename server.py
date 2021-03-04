from flask import Flask
from flask_restful import Api, Resource
from flask_cors import CORS
from booking import Booking
from check_perm import Check_perm
from hooking import Hooking
from qr_decode import Qr_decode
from my_mqtt import My_mqtt
from monitor import Monitor
from covid_log import Covid_log

class Server:
    app = None
    api = None
    meter = None
    monitor = None

    def __init__(self):
        print("init")
        self.app = Flask(__name__)
        CORS(self.app)
        self.api = Api(self.app)


if (__name__ == "__main__"):
    TAG = "main:"
    API_VERSION = "/api/v1"
    server = Server()
    monitor = Monitor()
    # my_mqtt = My_mqtt()

    server.api.add_resource(Check_perm, API_VERSION + "/check_perm/<room_num>")
    server.api.add_resource(Booking, API_VERSION + "/booking/<booking_number>")
    server.api.add_resource(Hooking, API_VERSION + "/hooking")
    server.api.add_resource(Qr_decode, API_VERSION + "/myqr")
    server.api.add_resource(My_mqtt, API_VERSION + "/unlock/<room_num>")
    server.api.add_resource(Covid_log, API_VERSION + "/covid/log")
    server.app.run(host="0.0.0.0", debug=False, port=5003)