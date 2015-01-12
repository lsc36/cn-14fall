#!/usr/bin/env python3

import tornado.ioloop
import tornado.web
from tornado.options import define, options, parse_command_line


define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")


class BaseHandler(tornado.web.RequestHandler):
    pass


class LoginHandler(BaseHandler):
    def post(self):
        pass


class RegisterHandler(BaseHandler):
    def post(self):
        pass


class RefreshHandler(BaseHandler):
    def post(self):
        pass


class UserListHandler(BaseHandler):
    def get(self):
        pass


class MakeRoomHandler(BaseHandler):
    def post(self):
        pass


class GetMessageHandler(BaseHandler):
    def get(self):
        pass


class SendMessageHandler(BaseHandler):
    def post(self):
        pass


class GetFileHandler(BaseHandler):
    def get(self):
        pass


class SendFileHandler(BaseHandler):
    def post(self):
        pass


def main():
    parse_command_line()
    app = tornado.web.Application(
        [
            (r"/login", LoginHandler),
            (r"/register", RegisterHandler),
            (r"/refresh", RefreshHandler),
            (r"/userlist", UserListHandler),
            (r"/mkroom", MakeRoomHandler),
            (r"/getmsg", GetMessageHandler),
            (r"/sendmsg", SendMessageHandler),
            (r"/getfile", GetFileHandler),
            (r"/sendfile", SendFileHandler),
            ],
        debug=options.debug,
        )
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__': main()
