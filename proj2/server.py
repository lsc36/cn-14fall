#!/usr/bin/env python3

import tornado.ioloop
import tornado.web
from tornado.options import define, options, parse_command_line
import atexit
import db


define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")
define("timeout", default=15, help="user timeout (secs)")
define("check_interval", default=5, help="interval of checking user timeout (secs)")
define("db", default="db.json", help="load/save database from/to file")


def require_token(func):
    def check_token_and_exec(*args, **kwargs):
        self = args[0]
        user = self.get_user()
        if not user:
            self.write({
                'result': False,
                'msg': 'Invalid token',
                })
        else:
            return func(*args, **kwargs)
    return check_token_and_exec


class BaseHandler(tornado.web.RequestHandler):
    def get_user(self):
        token = self.get_argument('token', default='')
        return db.get_user_from_token(token)


class LoginHandler(BaseHandler):
    def post(self):
        name = self.get_argument('user', default='')
        passwd = self.get_argument('pass', default='')
        token = db.user_login(name, passwd)
        if not token:
            self.write({
                'msg': 'Invalid username/password',
                })
        else:
            self.write({
                'token': token,
                'rooms': [],
                'msg': 'Login success',
                })


class RegisterHandler(BaseHandler):
    def post(self):
        name = self.get_argument('user', default='')
        passwd = self.get_argument('pass', default='')
        if not db.user_create(name, passwd):
            self.write({
                'result': False,
                'msg': 'Invalid username/password',
                })
        else:
            self.write({
                'result': True,
                'msg': 'Register success',
                })


class RefreshHandler(BaseHandler):
    @require_token
    def get(self):
        user = self.get_user()
        if not db.user_refresh(user['name']):
            self.write({
                'result': False,
                'msg': 'Refresh failed',
                })
        else:
            self.write({
                'result': True,
                'msg': 'Refresh success',
                })


class UserListHandler(BaseHandler):
    @require_token
    def get(self):
        self.write({
            'result': True,
            'userlist': db.get_user_list(),
            })


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
    db.load()
    atexit.register(db.save)
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
    check_logout_loop = tornado.ioloop.PeriodicCallback(
        db.check_logout, 1000 * options.check_interval
        )
    check_logout_loop.start()
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__': main()
