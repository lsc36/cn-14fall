#!/usr/bin/env python3

from ptt2 import PTT2
from input_parser import InputParser


def read_data():
    input_file = open('input.txt', 'r')
    parser = InputParser()
    data = parser.parse_all(input_file.read())
    input_file.close()
    return data


def main():
    data = read_data()
    ptt2 = PTT2(data['login']['id'], data['login']['pass'], True)


if __name__ == '__main__':
    main()
