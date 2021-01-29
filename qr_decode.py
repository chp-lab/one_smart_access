from flask_restful import Resource
from flask import send_from_directory
import requests

class Qr_decoder(Resource):
    def get(self):
        TAG = "qr_decode:"
        return send_from_directory("./public", "hello.txt")