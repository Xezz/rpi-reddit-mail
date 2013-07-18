rpi-reddit-mail
===============

A [reddit](https://www.reddit.com) mail notifier for the Raspberry Pi


Usage
=====

Edit mailnotifyer.py and set your username and password for reddit. To change the GPIO port ot use change pin_id to the value you want to use.
To start the application type `sudo python mailchecker.py`. I'd also suggest using screen (install it with `apt-get install screen`) and start
it with `screen sudo python mailchecker.py` and detach it with `CTRL + A D` (also see the manpage). screen -list to show all running screens,
screen -r to attach back to the screen (if only one screen is running)

Requirements
============

To use this you need to install RPi.GPIO and requests. I use pip for that:

 * sudo pip install RPi.GPIO
 * sudo pip install requests
