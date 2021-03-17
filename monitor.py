# -- coding: utf-8 --

from threading import Timer
from database import Database
from hooking import Hooking

class Monitor():
    def job(self):
        TAG = "Job:"
        alarm_start = 4
        alarm_end = 5
        cmd = """SELECT bookings.booking_number,users.one_id, bookings.one_email, bookings.meeting_start, bookings.meeting_end, bookings.agenda, bookings.room_num,
        (CURRENT_TIMESTAMP) AS cur_time, (TIME_TO_SEC(bookings.meeting_start) - TIME_TO_SEC((CURRENT_TIMESTAMP)))/60 AS minute_before_start, DATE_ADD(bookings.meeting_start, INTERVAL 30*60 SECOND) booking_time_out
        FROM bookings
        LEFT JOIN users ON bookings.one_email=users.one_email
        WHERE bookings.meeting_end > (CURRENT_TIMESTAMP) AND bookings.eject_at IS NULL AND (((TIME_TO_SEC(bookings.meeting_start) - TIME_TO_SEC((CURRENT_TIMESTAMP)))/60) > %s)
        AND (((TIME_TO_SEC(bookings.meeting_start) - TIME_TO_SEC((CURRENT_TIMESTAMP)))/60) <= %s)""" %(alarm_start, alarm_end)

        cmd_guest = """SELECT guests.booking_number, users.one_id, guests.guest_email, bookings.meeting_start, bookings.meeting_end, bookings.agenda, bookings.room_num, (CURRENT_TIMESTAMP) AS cur_time, (TIME_TO_SEC(bookings.meeting_start) - TIME_TO_SEC((CURRENT_TIMESTAMP)))/60 AS minute_before_start, DATE_ADD(bookings.meeting_start, INTERVAL 30*60 SECOND) booking_time_out
        FROM guests
        LEFT JOIN users ON guests.guest_email=users.one_email
        LEFT JOIN bookings ON guests.booking_number=bookings.booking_number
        WHERE bookings.meeting_end > (CURRENT_TIMESTAMP) AND bookings.eject_at IS NULL AND (((TIME_TO_SEC(bookings.meeting_start) - TIME_TO_SEC((CURRENT_TIMESTAMP)))/60) > %s)
        AND (((TIME_TO_SEC(bookings.meeting_start) - TIME_TO_SEC((CURRENT_TIMESTAMP)))/60) <= %s)""" %(alarm_start, alarm_end)

        database = Database()
        hooking = Hooking()

        res = database.getData(cmd)
        res2 = database.getData(cmd_guest)

        bookings = res[0]['result']
        guests = res2[0]['result']

        # print(TAG, "res=", res)
        print(TAG, "bookings=", bookings)
        for book in bookings:
            print(TAG, "book=", book)
            one_id = book['one_id']

            reply_msg = """การจองเลขที่ %s ของคุณ จะถึงเวลาเริ่ม %s สิ้นสุดเวลา %s ห้อง %s เหตุผล %s กรุณาเข้าห้องก่อนเวลา %s""" %(book['booking_number'], book['meeting_start'], book['meeting_end'], book['room_num'], book['agenda'], book['booking_time_out'])
            hooking.send_msg(one_id, reply_msg)

        for book in guests:
            print(TAG, "guest=", book)
            one_id = book['one_id']
            reply_msg = """คำเชิญจากเลขที่การจอง %s จะถึงเวลาเริ่ม %s สิ้นสุดเวลา %s ห้อง %s เหตุผล %s เรียนเชิญเข้าร่วมค่ะ""" %(book['booking_number'], book['meeting_start'], book['meeting_end'], book['room_num'], book['agenda'])
            hooking.send_msg(one_id, reply_msg)

        cmd_eject = """SELECT bookings.booking_number, users.one_id, bookings.one_email, bookings.meeting_start, bookings.meeting_end, bookings.agenda, bookings.room_num, (CURRENT_TIMESTAMP) AS cur_time,
        (TIME_TO_SEC((CURRENT_TIMESTAMP)) - (TIME_TO_SEC(bookings.meeting_start)))/60 AS minute_after_start, access_logs.log_id, access_logs.one_email AS access_by, access_logs.created_at AS acess_at
        FROM bookings
        LEFT JOIN users ON bookings.one_email=users.one_email
        LEFT JOIN access_logs ON bookings.booking_number=access_logs.booking_number
        WHERE bookings.meeting_end > (CURRENT_TIMESTAMP) AND bookings.eject_at IS NULL AND access_logs.one_email IS NULL AND 
        ((TIME_TO_SEC(CURRENT_TIMESTAMP) - TIME_TO_SEC(bookings.meeting_start))/60 >= 30) AND bookings.meeting_start < (CURRENT_TIMESTAMP)"""

        res_eject = database.getData(cmd_eject)
        ejectings = res_eject[0]['result']
        for eject in ejectings:
            print(TAG, "eject=", eject)
            one_id = eject['one_id']
            reply_msg = """ขออภัยค่ะ ท่านหรือแขกของท่านไม่ได้เข้าใช้การจองเลขที่ %s ในเวลาที่กำหนด เริ่มเวลา %s สิ้นสุดเวลา %s ห้อง %s เหตุผล %s ระบบจะยกเลิกการจองโดยอัตโนมัติ กรุณาทำการจองใหม่ ขอบคุณค่ะ""" \
                        %(eject['booking_number'], eject['meeting_start'], eject['meeting_end'], eject['room_num'], eject['agenda'])
            hooking.send_msg(one_id, reply_msg)
            cmd_update = """UPDATE `bookings` SET `eject_at` = CURRENT_TIMESTAMP WHERE `bookings`.`booking_number` = %s""" %(eject['booking_number'])
            insert = database.insertData(cmd_update)
            print(TAG, "insert=",insert)
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
