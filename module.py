
class Module():
    def __init__(self):
        print("Creating new modules")

    def measurementNotFound(self):
        return {
                   'type': False,
                   'message': "fail",
                   'error_message': "Not Found",
                   'result': None
               }, 404

    def serveErrMsg(self):
        return {
                   'type': False,
                   'message': "fail",
                   'error_message': "Internal Server Error",
                   'result': None
               }, 500

    def isQueryStr(self, args, key):
        TAG = "isQueryStr:"
        # print(TAG, "args=", args, type(args))
        if ((args.get(key) is not None) and (len(args.get(key)) > 0)):
            return True
        else:
            return False

    def unauthorized(self):
        return {
                   'type': False,
                   'message': "fail",
                   'error_message': "Unauthorized",
                   'result': None
               }, 401

    def userNotFound(self):
        return {
                   'type': False,
                   'message': "fail",
                   'error_message': "User not found",
                   'result': None
               }, 404

    def isValidToken(self, current_user):
        if("sub" not in current_user):
            return False
        else:
            return True

    def wrongAPImsg(self):
        return {
                   'type': False,
                   'message': "fail",
                   'error_message': "wrong API calling. Check related parameter e.g. query string, url etc.",
                   'result': None
               }, 400
    def meterExist(self):
        return {
                   'type': False,
                   'message': "fail",
                   'error_message': "Meter exist",
                   'result': None
               }, 400

