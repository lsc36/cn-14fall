from telnetlib import Telnet


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
