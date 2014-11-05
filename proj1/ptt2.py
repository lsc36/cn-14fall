from telnetlib import Telnet


class PTT2(Telnet):

    def read_until(self, expected, timeout=None):
        """Print bytes read if debug flag is set"""
        s = super().read_until(expected, timeout=None)
        if self.debug: print(s)

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
        self.read_very_eager()  # read everyting left
