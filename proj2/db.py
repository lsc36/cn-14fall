import os
import time
import logging
import json
from hashlib import sha256
from tornado.concurrent import Future
from tornado.options import options

users = {}
login_users = {}
rooms = {}
rooms_by_hash = {}
files = {}

logger = logging.getLogger()


def load():
    global users, rooms, rooms_by_hash, files
    if not options.db: return
    try:
        with open(options.db, 'r') as f:
            db = json.loads(f.read())
        users = db['users']
        rooms_by_hash = db['rooms']
        for room_hash, room in rooms_by_hash.items():
            rooms[room['id']] = room
        files = db['files']
        logging.info('Database loaded from %s' % options.db)
    except RuntimeError:
        logging.warning('Error loading database from %s, use empty' % options.db)


def save():
    if not options.db: return
    db = {'users': {}, 'rooms': {}}
    for name, userinfo in users.items():
        userinfo_c = userinfo.copy()
        userinfo_c['login_token'] = ''
        db['users'][name] = userinfo_c
    for room_hash, room in rooms_by_hash.items():
        room_c = room.copy()
        room_c['waiters'] = []
        db['rooms'][room_hash] = room_c
    db['files'] = files
    try:
        with open(options.db, 'w') as f:
            f.write(json.dumps(db))
        logging.info('Database saved to %s' % options.db)
    except:
        logging.error('Error saving database to %s' % options.db)


def get_user_from_token(token):
    try:
        return login_users[token]
    except KeyError:
        return False


def user_login(name, passwd):
    try:
        if users[name]['passwd_sha256'] == sha256(passwd.encode()).hexdigest():
            if users[name]['login_token']:
                users[name]['last_refresh'] = time.time()
                return users[name]['login_token']
            token = sha256(os.urandom(64)).hexdigest()
            users[name]['login_token'] = token
            users[name]['last_refresh'] = time.time()
            login_users[token] = users[name]
            logging.info('User %s logged in' % name)
            return token
        else:
            return False
    except KeyError:
        return False


def user_create(name, passwd):
    if not name or not passwd: return False
    if name in users: return False
    users[name] = {
        'name': name,
        'passwd_sha256': sha256(passwd.encode()).hexdigest(),
        'login_token': '',
        'last_refresh': time.time(),
        'rooms': [],
        }
    logging.info('User %s created' % name)
    return True


def user_refresh(name):
    try:
        users[name]['last_refresh'] = time.time()
        return True
    except KeyError:
        return False


def check_logout():
    for token, userinfo in list(login_users.items()):
        if userinfo['last_refresh'] + options.timeout < time.time():
            userinfo['login_token'] = ''
            login_users.pop(token)
            logging.info('User %s logged out' % userinfo['name'])


def get_user_list():
    userlist = []
    for name, userinfo in users.items():
        userlist.append({
            'name': name,
            'online': userinfo['login_token'] != '',
            })
    return userlist


def create_room(userlist):
    userlist.sort()
    hsh = sha256()
    for name in userlist: hsh.update(name.encode() + b'#')
    room_hash = hsh.hexdigest()
    if room_hash not in rooms_by_hash:
        room_id = sha256(os.urandom(64)).hexdigest()
        rooms_by_hash[room_hash] = {
            'id': room_id,
            'users': userlist,
            'msgs': [],
            'waiters': [],
            }
        for name in userlist:
            users[name]['rooms'].append(room_id)
        rooms[room_id] = rooms_by_hash[room_hash]
        logging.info("Room created with users %s" % ', '.join(userlist))
    return rooms_by_hash[room_hash]['id']


def get_room_users(room_id):
    return rooms[room_id]['users']


def get_messages_since(room_id, last_time):
    for i in range(len(rooms[room_id]['msgs'])):
        if rooms[room_id]['msgs'][i]['time'] > last_time:
            return rooms[room_id]['msgs'][i:]
    return []


def wait_for_messages(room_id):
    future = Future()
    rooms[room_id]['waiters'].append(future)
    return future


def cancel_wait(room_id, future):
    rooms[room_id]['waiters'].remove(future)


def send_message(room_id, user, msg):
    msg_entry = {
        'time': time.time(),
        'from': user['name'],
        'msg': msg,
        }
    rooms[room_id]['msgs'].append(msg_entry)
    for waiter in rooms[room_id]['waiters']:
        waiter.set_result([msg_entry])
    rooms[room_id]['waiters'] = []


def add_file(filename, content):
    hsh = sha256(content).hexdigest()
    with open('uploads/' + hsh, 'wb') as f:
        f.write(content)
    files[hsh] = {
        'name': filename,
        }
    logging.info("File %s (%s) uploaded" % (filename, hsh))
    return hsh


def get_file(hsh):
    if hsh not in files:
        return False
    with open('uploads/' + hsh, 'rb') as f:
        content = f.read()
    return {
        'name': files[hsh]['name'],
        'content': content,
        }
