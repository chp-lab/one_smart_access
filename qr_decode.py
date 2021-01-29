from flask_restful import Resource
from flask import send_from_directory, request
import requests

class Qr_decode(Resource):
    def get(self):
        TAG = "qr_decode:"
        return send_from_directory("./public", "tmpqrcode.png")
    def post(self):
        TAG = "qr_code_hd:"
        uploaded_file = request.files['file']
        if(uploaded_file.filename != ''):
            uploaded_file.save("./public/tmpqrcode.png")
            return "testing"