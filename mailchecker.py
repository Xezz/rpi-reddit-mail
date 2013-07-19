#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Xezz'
__version__ = '0.3'

import sys
import time
import logging
from datetime import datetime

import requests

from RPi import GPIO



# This is the user agent shown to reddit
user_agent = '%s Loomax RPi mail notifier /u/Loomax' % __version__
# credentials to login, reddit username and password
user_name = ''
password = ''
# Which pin to toggle when new mail arrives, or mail has been read
pin_id = 11
# 60s is 1 minute :P
minutes_to_seconds = 60
# wait 5 minutes
default_wait_time = 5 * minutes_to_seconds
# Start throttle at 2 am
__throttle_start = {'hour': 2, 'minute': 0}
# stop throttle at 9:30
__throttle_end = {'hour': 9, 'minute': 30}
throttle_start = __throttle_start['hour'] * 60 + __throttle_start['minute']
throttle_end = __throttle_end['hour'] * 60 + __throttle_end['minute']
# not throttled then wait for 5 minutes
speed_normal = 5 * minutes_to_seconds
#  throttled then don't refresh for the difference / 2
throttled_wait_time = (throttle_end - throttle_start) * 30
if throttled_wait_time < default_wait_time:
    throttled_wait_time = default_wait_time


def getSleepTime():
    """Check what kind of throttle in seconds we have ot return

    Checks if the current time is within the sleep time and returns the correct sleep time
    """
    right_now = datetime.now()
    minutes_now = right_now.hour * 60 + right_now.minute
    if minutes_now >= throttle_start and minutes_now < throttle_end:
        return throttled_wait_time
    else:
        return default_wait_time


def switchLight(has_new_mail):
    GPIO.output(pin_id, has_new_mail)


def main():
    # Enable logging
    logging.basicConfig(filename='checkerr.log', format='[%(levelname)s]:%(name)s %(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    logging.info('Starting mailchecker on pin %d' % pin_id)
    logger = logging.getLogger(__name__)
    # Using board layout
    GPIO.setmode(GPIO.BOARD)
    # set the pin to output
    GPIO.setup(pin_id, GPIO.OUT)

    session = requests.Session()
    session.headers.update({'User-Agent': user_agent})
    first_run = True
    try:
        session.post('https://ssl.reddit.com/api/login',
                     data={'user': user_name, 'passwd': password, 'api_type': 'json'})
    except requests.exceptions.RequestException as re:
        logger.warn('Failed to connect to reddit. Message: %s' % re.message)
        sys.exit(1)
    while True:
        try:
            # Reddit is caching pages for 30s, so no need to request more often than that
            # First request is fine to run tho!
            if not first_run:
                time.sleep(getSleepTime())
            else:
                first_run = False
            logger.debug('Fetching data about myself')
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
                    if has_mail:
                        logger.info('New mail arrived!')
                except Exception as e:
                    logger.warn('Unexpected error while trying to parse json. Type: %s, Message: %s' % e.__class__,
                                e.message)
            else:
                logger.warn('Status code was not 200 it was [%s]' % r.status_code)
        except (KeyboardInterrupt, SystemExit):
            # Clean up (resetting those GPIO's that got used in this script)
            GPIO.cleanup()
            break


if __name__ == "__main__":
    main()