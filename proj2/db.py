import os
import time
import logging
from hashlib import sha256

users = {}
login_users = {}

logger = logging.getLogger()


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
