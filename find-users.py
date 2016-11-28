#!/usr/bin/env python
# encoding: utf-8
import requests
from pyquery import PyQuery as pq
import json
import grequests
import logging
import os
import signal
import sys
import argparse
# import pinyin
# import copy


CITY_DIR = 'city'
LANG_DIR = 'language'

# disable requests log
# logging.getLogger('requests').setLevel(logging.WARNING)

def setup_logging():
    # set logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    return logger


# handle Ctrl+C
def signal_handler(signal, frame):
    logger.warning('Got Ctrl+C, exit ...')
    sys.exit(0)

logger = setup_logging()
signal.signal(signal.SIGINT, signal_handler)
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
}


def search_users(loc, lang=None, page=1):
    users = []

    while True:
        if lang:
            url = ('https://github.com/search?l={lang}&langOverride=&'
                   'language={lang}&q=location:{loc}&type=Users'
                   .format(lang=lang, loc=loc, page=page)
                  )
        else:
            url = ('https://github.com/search?langOverride=&language=&type=Users'
                   '&q=location:{}'.format(loc)
                  )

        msg = ('location: {}, language: {}, page: {}'.format(loc, lang, page))
        logger.debug(msg)
        url = '{url}&p={page}'.format(url=url, page=page)
        req = requests.get(url, headers=headers)
        if req.status_code != 200:
            # github rate limit
            if req.status_code == 429:
                logger.debug('githut rate limit: {msg}'.format(msg=msg))
            # no more page
            if req.status_code == 404:
                logger.debug('no more page ..., exit!')
                return -1, users
        else:
            doc = pq(req.content)
            users.extend([user.text for user in doc('div.user-list-info > a')])
            page += 1

    return page, users


def get_users_info(users):

    '''
    get user info by username.

    $ curl -L https://api.github.com/users/c9s -H "Accept: application/vnd.github.full+json"
    '''

    urls = ['https://api.github.com/users/{}'.format(username) for username
            in users
           ]

    while True:
        users_info = None
        try:
            rs = (grequests.get(url, headers=headers) for url in urls)
            users_info = [req.json() for req in grequests.map(rs) if req.status_code == 200]
        except AttributeError:
            logger.debug('got AttributeError exception, retry ...')
            pass

        if users_info:
            break

    return users_info


def fetch_users(loc, lang=None, page=1):
    res = []

    if lang:
        page, users = search_users(loc, lang=lang, page=page)
    else:
        page, users = search_users(loc, page=page)

    users_info = get_users_info(users)
    res.extend(users_info)

    return page, res


def generate_city_json(locations):
    for loc in locations:
        data = []
        page = 1

        while True:
            page, res = fetch_users(loc, page=page)
            if res:
                data.extend(res)
            if page < 0:
                logger.debug('no more data, exit.')
                break

        if not os.path.exists(CITY_DIR):
            os.mkdir(CITY_DIR)
        fname = os.path.join(CITY_DIR, '{}.json'.format(loc))
        fd = open(fname, 'w')
        json.dump(data, fd, ensure_ascii=False)
        fd.close()


def generate_lang_json(langs, loc='China'):
    for lang in langs:
        data = []
        page = 1

        while True:

            page, res = fetch_users(loc, lang=lang, page=page)
            if res:
                data.extend(res)
            if page < 0:
                logger.debug('no more data, exit.')
                break

        if not os.path.exists(LANG_DIR):
            os.mkdir(LANG_DIR)
        fname = os.path.join(LANG_DIR, '{}-{}.json'.format(loc, lang))
        fd = open(fname, 'w')
        json.dump(data, fd, ensure_ascii=False)
        fd.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='fetch github users by location or language'
    )
    parser.add_argument('-p', '--position', nargs='+',
                        help='home position/location/city',
                        required=True)
    parser.add_argument('-l', '--language', nargs='+',
                        help='computer language, e.g.: Java, Python',
                        required=False)
    # parser.add_argument('-c', '--convert', help='Convert chinese to pinyin',
    #                     action='store_true', required=False)
    # parser.set_defaults(convert=True)
    args  = parser.parse_args()
    langs = args.language
    locations = args.position

    # pinyin这个module对多音字处理的不好，比如：重庆 -> zhongqing
    # locations = copy.copy(positions)
    # if args.convert:
    #     for pos in positions:
    #         if pos[0] > u'\u4e00' and pos[0] < u'\u9fff':
    #             locations.insert(locations.index(pos),
    #                              pinyin.get(pos, format='strip')
    #                             )

    logger.debug('developer home location: {}'.format(locations))
    logger.debug('computer languages: {}'.format(langs))

    if langs:
        for loc in locations:
            generate_lang_json(langs, loc=loc)
    else:
        generate_city_json(locations)
