#!/usr/bin/env python
# encoding: utf-8
import json
import os
import argparse


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='merge json files.')
    parser.add_argument('-i', '--input', nargs='+', help='Input json files',
                        required=True)
    parser.add_argument('-o', '--output', help='Output json file name',
                        required=True)
    args = parser.parse_args()

    res = []
    for f in args.input:
        if os.path.exists(f):
            fd = open(f)
            data = json.load(fd)
            res.extend(data)
        else:
            print('can not find file: <{}>, skiping ...'.format(f))

    sorted_res = sorted(res, key=lambda k: k['followers'], reverse=True)
    fd = open(args.output, 'w')
    json.dump(sorted_res, fd, ensure_ascii=False)
    fd.close()
