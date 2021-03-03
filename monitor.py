# -- coding: utf-8 --

from threading import Timer
from database import Database
from hooking import Hooking

class Monitor():
    def job(self):
        TAG = "Job:"
        print(TAG, "Hello")
        cmd = """SELECT bookings.booking_number,users.one_id, bookings.one_email, bookings.meeting_start, bookings.meeting_end, bookings.agenda, bookings.room_num,
        (CURRENT_TIMESTAMP) AS cur_time, (TIME_TO_SEC(bookings.meeting_start) - TIME_TO_SEC((CURRENT_TIMESTAMP)))/60 AS minute_before_start, DATE_ADD(bookings.meeting_start, INTERVAL 30*60 SECOND) booking_time_out
        FROM bookings
        LEFT JOIN users ON bookings.one_email=users.one_email
        WHERE bookings.meeting_end > (CURRENT_TIMESTAMP) AND bookings.eject_at IS NULL AND (((TIME_TO_SEC(bookings.meeting_start) - TIME_TO_SEC((CURRENT_TIMESTAMP)))/60) > 5)
        AND (((TIME_TO_SEC(bookings.meeting_start) - TIME_TO_SEC((CURRENT_TIMESTAMP)))/60) <= 6)"""

        database = Database()
        hooking = Hooking()

        res = database.getData(cmd)
        bookings = res[0]['result']
        # print(TAG, "res=", res)
        print(TAG, "bookings=", bookings)
        for book in bookings:
            print(TAG, "book=", book)
            one_id = book['one_id']

            reply_msg = """การจองเลขที่ %s ของคุณกำลังจะถึงเวลาเริ่ม %s สิ้นสุดเวลา %s ห้อง %s เหตุผล %s กรุณาเข้าห้องก่อนเวลา %s""" %(book['booking_number'], book['meeting_start'], book['meeting_end'], book['room_num'], book['agenda'], book['booking_time_out'])
            hooking.send_msg(one_id, reply_msg)

        return False

    def setInterval(self, timer, task):
        TAG = "Monitor:"
        isStop = task()
        if not isStop:
            print(TAG, "time to run")
            Timer(timer,self.setInterval, [timer, task]).start()

    def __init__(self):
        TAG = "Monitor init:"
        print(TAG, "initialize")
        self.setInterval(60.0, self.job)

if __name__ == "__main__":
    TAG = "main mopnitor:"
    print(TAG, "start monitoring")
    monitor = Monitor()
    while True:
        pass
