from html.parser import HTMLParser


class InputParser(HTMLParser):

    def handle_starttag(self, tag, attrs):
        if tag == 'id': self.idx1 = 'login'
        elif tag == 'board': self.idx1 = 'post'
        elif tag == 'w': self.idx1 = 'waterball'
        elif tag == 'm': self.idx1 = 'mail'

        if tag == 'w' or tag == 'm': self.idx2 = 'id'
        elif tag == 'p': self.idx2 = 'title'
        else: self.idx2 = tag

    def handle_endtag(self, tag):
        self.idx2 = None

    def handle_data(self, data):
        if self.idx1 and self.idx2:
            self.data[self.idx1][self.idx2] = data.replace('\n', '\r\n')

    def parse_all(self, s):
        self.data = {idx1: dict()
            for idx1 in ['login', 'post', 'waterball', 'mail']}
        self.idx1 = self.idx2 = None
        self.feed(s)
        return self.data
