#!/usr/bin/env python3

from ptt2 import PTT2


def read_data():
    data = dict()
    from getpass import getpass
    data['user'] = input("User: ")
    data['passwd'] = getpass()
    return data


def main():
    data = read_data()
    ptt2 = PTT2(data['user'], data['passwd'], True)


if __name__ == '__main__':
    main()
