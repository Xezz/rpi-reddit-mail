#!/usr/bin/env python
import requests
import time
from RPi import GPIO

__author__ = 'Xezz'

# This is the user agent shown to reddit
user_agent = '0.2 Loomax RPi mail notifier /u/Loomax'
# credentials to login, reddit username and password
user_name = ''
password = ''
# Which pin to toggle when new mail arrives, or mail has been read
pin_id = 13


def switchLight(has_new_mail):
    GPIO.output(pin_id, has_new_mail)


def main():
    # Using board layout
    GPIO.setmode(GPIO.BOARD)
    # set the pin to output
    GPIO.setup(pin_id, GPIO.OUT)

    session = requests.Session()
    session.headers.update({'User-Agent': user_agent})
    session.post('https://ssl.reddit.com/api/login', data={'user': user_name, 'passwd': password, 'api_type': 'json'})
    while True:
        r = session.get('https://ssl.reddit.com/api/me.json')
        request_as_json = r.json()
        has_mail = request_as_json['data']['has_mail']
        switchLight(has_mail)
        # Reddit is caching pages for 30s, so no need to request more often than that
        time.sleep(45)
    # Clean up (resetting those GPIO's that got used in this script)
    GPIO.cleanup()

if __name__ == "__main__":
    main()