from telnetlib import Telnet


CTRL_P = b'\x10'
CTRL_X = b'\x18'
ARROW_UP = b'\x1b[A'
ARROW_DOWN = b'\x1b[B'
ARROW_LEFT = b'\x1b[D'
ARROW_RIGHT = b'\x1b[C'


class PTT2(Telnet):

    def read_until(self, expected, timeout=None):
        """Print bytes read if debug flag is set"""
        s = super().read_until(expected, timeout=None)
        if self.debug: print('read %d bytes: %s' % (len(s), s))
        return s

    def read_very_eager(self):
        """Print bytes read if debug flag is set"""
        s = super().read_very_eager()
        if self.debug: print('read %d bytes: %s' % (len(s), s))
        return s

    def write(self, buf):
        """Print bytes written if debug flag is set"""
        super().write(buf)
        if self.debug: print('write %d bytes: %s' % (len(buf), buf))

    def read_everything_left(self):
        while self.read_very_eager(): pass

    def __init__(self, user, passwd, debug=False):
        """Connect and login"""
        super().__init__('ptt2.cc')
        self.debug = debug

        self.read_until('註冊:'.encode('big5'))
        self.write(user.encode('big5') + b'\r\n')
        self.read_until('密碼:'.encode('big5'))
        self.write(passwd.encode('big5') + b'\r\n')
        self.read_until('請按任意鍵繼續'.encode('big5'))
        self.write(b'\r\n')
        self.read_until('呼叫器'.encode('big5'))
        self.read_everything_left()

    def goto_main_menu(self):
        self.write(ARROW_LEFT * 10)
        self.read_everything_left()

    def post(self, board, title, content):
        """Post to given board with title and content"""
        # goto board
        self.goto_main_menu()
        self.write(b's' + board.encode('big5') + b'\r\n')
        # TODO: handle splashscreen
        self.read_until('進板畫面'.encode('big5'))
        self.read_everything_left()

        # post
        self.write(CTRL_P + b'\r\n')
        self.read_until('標題：'.encode('big5'))
        self.write(title.encode('big5') + b'\r\n')
        self.read_until(b'1:  1')
        self.write(content.encode('big5'))
        self.write(CTRL_X + b'\r\n')
        self.read_until('請按任意鍵繼續'.encode('big5'))
        self.write(b'\r\n')
        self.read_until('進板畫面'.encode('big5'))
        self.read_everything_left()

    def mail(self, user_id, title, content):
        # goto mailbox
        self.goto_main_menu()
        self.write(b'm' + ARROW_RIGHT * 2)
        self.read_until('離開'.encode('big5'))
        self.read_everything_left()

        # send mail
        self.write(CTRL_P)
        self.read_until('代號'.encode('big5'))
        self.write(user_id.encode('big5') + b'\r\n')
        self.read_until('主題：'.encode('big5'))
        self.write(title.encode('big5') + b'\r\n')
        self.read_until(b'1:  1')
        self.write(content.encode('big5'))
        self.write(CTRL_X + b'\r\n')
        self.read_until(b'[N]')
        self.write(b'\r\n')
        self.read_until('請按任意鍵繼續'.encode('big5'))
        self.write(b'\r\n')
        self.read_until('離開'.encode('big5'))
        self.read_everything_left()
