import os
import time
import logging
import json
from hashlib import sha256
from tornado.options import options

users = {}
login_users = {}

logger = logging.getLogger()


def load():
    global users
    if not options.db: return
    try:
        with open(options.db, 'r') as f:
            db = json.loads(f.read())
        users = db['users']
        logging.info('Database loaded from %s' % options.db)
    except:
        logging.warning('Error loading database from %s, use empty' % options.db)


def save():
    if not options.db: return
    db = {'users': {}}
    for name, userinfo in users.items():
        userinfo_c = userinfo.copy()
        userinfo_c['login_token'] = ''
        db['users'][name] = userinfo_c
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
                login_users[users[name]['login_token']]['last_refresh'] = time.time()
                return users[name]['login_token']
            token = sha256(os.urandom(64)).hexdigest()
            users[name]['login_token'] = token
            login_users[token] = {'name': name, 'last_refresh': time.time()}
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
        'passwd_sha256': sha256(passwd.encode()).hexdigest(),
        'login_token': '',
        }
    logging.info('User %s created' % name)
    return True


def user_refresh(name):
    try:
        token = users[name]['login_token']
        login_users[token]['last_refresh'] = time.time()
        return True
    except KeyError:
        return False


def check_logout():
    for token, userinfo in list(login_users.items()):
        if userinfo['last_refresh'] + options.timeout < time.time():
            users[userinfo['name']]['login_token'] = ''
            login_users.pop(token)
            logging.info('User %s logged out' % userinfo['name'])
