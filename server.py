from flask import Flask
from  flask_restful import Api,Resource
from flask_cors import CORS
from booking import Booking
from check_perm import Check_perm
from hooking import Hooking

class Server:
    app = None
    api = None
    meter = None

    def __init__(self):
        print("init")
        self.app = Flask(__name__)
        CORS(self.app)
        self.api = Api(self.app)

if(__name__ == "__main__"):
    TAG = "main:"
    API_VERSION = "/api/v1"
    server = Server()
    server.api.add_resource(Check_perm, API_VERSION + "/check_perm/<room_num>")
    server.api.add_resource(Booking, API_VERSION + "/booking/<booking_number>")
    server.api.add_resource(Hooking, API_VERSION + "/hooking")
    
    server.app.run(host="0.0.0.0", debug=True, port=5003)