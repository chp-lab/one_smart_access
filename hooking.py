from flask_restful import Resource, reqparse
from flask import Flask, request, jsonify
import time
from database import Database

class Hooking(Resource):
    def post(self):
        TAG = "Hooking:"
        data = request.json
        print(TAG, data)

        return {
            "type": True,
            "message": "success",
            "elapsed_time_ms": 0,
            "len": 0,
            "result": "testing"
        }
