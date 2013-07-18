#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

__author__ = 'Xezz'

import requests
import time
import logging
from RPi import GPIO


# This is the user agent shown to reddit
user_agent = '0.2 Loomax RPi mail notifier /u/Loomax'
# credentials to login, reddit username and password
user_name = ''
password = ''
# Which pin to toggle when new mail arrives, or mail has been read
pin_id = 11


def switchLight(has_new_mail):
    GPIO.output(pin_id, has_new_mail)


def main():
    # Enable logging
    logging.basicConfig(filename='checkerr.log', format='[%(severity)s]%(logger)s:%(name)s %(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    logging.info('Starting mailchecker on pin %d' % pin_id)
    logger = logging.getLogger(__name__)
    # Using board layout
    GPIO.setmode(GPIO.BOARD)
    # set the pin to output
    GPIO.setup(pin_id, GPIO.OUT)

    session = requests.Session()
    session.headers.update({'User-Agent': user_agent})
    try:
        session.post('https://ssl.reddit.com/api/login',
                     data={'user': user_name, 'passwd': password, 'api_type': 'json'})
    except requests.exceptions.RequestException as re:
        logger.warn('Failed to connect to reddit. Message: %s' % re.message)
        sys.exit(1)
    while True:
        # Reddit is caching pages for 30s, so no need to request more often than that
        time.sleep(45)
        logger.info('Fetching data about myself')
        try:
            r = session.get('https://ssl.reddit.com/api/me.json')
        except requests.exceptions.RequestException as re:
            logger.warn('Failed to fetch me.json. error: %s' % re.message)
            continue

        if r.status_code == 200:
            try:
                request_as_json = r.json()
                has_mail = request_as_json['data']['has_mail']
                switchLight(has_mail)
            except Exception as e:
                logger.warn('Unexpected error while trying to parse json. Type: %s, Message: %s' % e.__class__,
                            e.message)
        else:
            logger.info('Status code was not 200 it was [%s]' % r.status_code)

    # Clean up (resetting those GPIO's that got used in this script)
    GPIO.cleanup()


if __name__ == "__main__":
    main()