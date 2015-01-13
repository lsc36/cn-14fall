#!/usr/bin/env python3

import tornado.ioloop
import tornado.web
import tornado.gen
from tornado.options import define, options, parse_command_line
import logging
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
                'rooms': db.get_user_from_token(token)['rooms'],
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
    @require_token
    def post(self):
        user = self.get_user()
        room_userlist = self.get_arguments('user')
        if len(room_userlist) < 2:
            self.write({
                'result': False,
                'msg': 'Should provide more than 2 users',
                })
            return
        for roomuser in room_userlist:
            if roomuser not in db.users:
                self.write({
                    'result': False,
                    'msg': 'User %s does not exist' % roomuser,
                    })
                return
        self.write({
            'result': True,
            'room_id': db.create_room(room_userlist),
            })


class GetMessageHandler(BaseHandler):
    @require_token
    @tornado.gen.coroutine
    def get(self):
        room_id = self.get_argument('room_id', default='')
        last_time = self.get_argument('last', default='0.0')
        if room_id not in db.rooms:
            self.write({
                'result': False,
                'msg': 'Invalid room id',
                })
            return
        try:
            last_time = float(last_time)
        except ValueError:
            self.write({
                'result': False,
                'msg': 'Invalid room id',
                })
            return
        msgs = db.get_messages_since(room_id, last_time)
        if msgs:
            self.write({
                'result': True,
                'msgs': msgs,
                })
        else:
            self.room_id = room_id
            self.future = db.wait_for_messages(room_id)
            msgs = yield self.future
            self.write({
                'result': True,
                'msgs': msgs,
                })

    def on_connection_close(self):
        db.cancel_wait(self.room_id, self.future)


class SendMessageHandler(BaseHandler):
    @require_token
    def post(self):
        room_id = self.get_argument('room_id', default='')
        msg = self.get_argument('msg', default='')
        if room_id not in db.rooms:
            self.write({
                'result': False,
                'msg': 'Invalid room id',
                })
            return
        if not msg:
            self.write({
                'result': False,
                'msg': 'Empty message',
                })
            return
        db.send_message(room_id, self.get_user(), msg)
        self.write({
            'result': True,
            'msg': 'Send message success',
            })


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
