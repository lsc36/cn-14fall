#!/usr/bin/env python3

from ptt2 import PTT2
from input_parser import InputParser
import sys


def read_data():
    input_file = open(sys.argv[1])
    parser = InputParser()
    data = parser.parse_all(input_file.read())
    input_file.close()
    return data


def main():
    data = read_data()
    print("Logging in as %s ..." % (data['login']['id']))
    ptt2 = PTT2(data['login']['id'], data['login']['pass'])
    print("Posting article on board %s, title: %s ..."
        % (data['post']['board'], data['post']['title']))
    ptt2.post(data['post']['board'], data['post']['title'],
        data['post']['content'])
    print("Sending mail to %s, title: %s ..."
        % (data['mail']['id'], data['mail']['title']))
    ptt2.mail(data['mail']['id'], data['mail']['title'],
        data['mail']['content'])
    print("Sending waterball to %s, content: %s ..."
        % (data['waterball']['id'], data['waterball']['content']))
    ptt2.waterball(data['waterball']['id'], data['waterball']['content'])
    print("Checking new mails...")
    newmail_list = ptt2.get_newmail_list()
    if not newmail_list: print("No new mails")
    for mail in newmail_list:
        print("Mail ID: %s From: %s Title: %s"
            % (mail['id'], mail['from'], mail['title']))
        print("== Begin mail ==")
        print(mail['content'])
        print("== End of mail ==")
    print("Waiting for waterball...")
    wb = ptt2.get_waterball()
    print("Waterball from: %s content: %s" % (wb['from'], wb['content']))

    ptt2.close()


if __name__ == '__main__':
    main()
