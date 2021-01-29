from flask_restful import Resource
from flask import send_from_directory, request
import requests

class Qr_decode(Resource):
    file_name = "tmpqrcode.jpg"
    file_path = "./public"
    def get(self):
        TAG = "qr_decode:"
        return send_from_directory(self.file_path, self.file_name)
    def post(self):
        TAG = "qr_code_hd:"
        uploaded_file = request.files['file']
        if(uploaded_file.filename != ''):
            uploaded_file.save(self.file_path + "/" + self.file_name)
            return "testing"