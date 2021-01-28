from flask_restful import Resource, reqparse
import time
from database import Database

class Booking(Resource):
    def get(self, booking_number):
        TAG = "Booking:"
        start_time = time.time()
        database = Database()

        cmd = """SELECT * FROM bookings WHERE booking_number=%s""" %(booking_number)
        res = database.getData(cmd)

        elapsed_time = (time.time() - start_time) * 1000
        print(TAG, "times=", elapsed_time, "ms")

        return {
            "type": True,
            "message": "success",
            "elapsed_time_ms": elapsed_time,
            "len": len(res),
            "result": res
        }
