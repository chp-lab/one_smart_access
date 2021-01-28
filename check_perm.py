from flask_restful import Resource, reqparse
import time
from database import Database
from module import Module

class Check_perm(Resource):
    def post(self, room_num):
        TAG = "Check_perm:"
        module = Module()
        database = Database()

        start_time = time.time()
        booking_key = "booking_number"
        one_id_key = "one_id"

        parser = reqparse.RequestParser()

        parser.add_argument(booking_key)
        parser.add_argument(one_id_key)

        args = parser.parse_args()

        if (not (module.isQueryStr(args, one_id_key) or module.isQueryStr(args, booking_key))):
            print(TAG, "bad req")
            return module.wrongAPImsg()

        booking_number = args.get(booking_key)
        one_id = args.get(one_id_key)

        # check with database

        query_cmd = """ SELECT IF((CURRENT_TIMESTAMP>bookings.meeting_start) AND (CURRENT_TIMESTAMP<bookings.meeting_end), true, false) as time_to_meet FROM bookings WHERE booking_number=%s AND one_email='%s' AND room_num='%s' """ \
                    % (booking_number, one_id, room_num)
        print(TAG, "query_cmd=", query_cmd)
        response = database.getData(query_cmd)
        print(TAG, "result=", response)
        # check error
        if (response[1] != 200):
            return response
        # user not found
        if (len(response[0]['result']) == 0):
            print(TAG, "booking not found!")
            return module.measurementNotFound()

        result = response[0]['result']
        access_perm = result[0]["time_to_meet"]


        elapsed_time = (time.time() - start_time) * 1000
        print(TAG, "times=", elapsed_time, "ms")

        return {
                   'type': True,
                   'message': "success",
                   'elapsed_time_ms': elapsed_time,
                   'len': len(result),
                   'result': result,
               }, 200
