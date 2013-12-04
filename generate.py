# Copyright (c) 2013 Michael Bikovitsky

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import json
import re
import configparser
import argparse
import sys
from datetime import datetime
from urllib.parse import urlparse
from urllib.request import urlopen
from bs4 import BeautifulSoup, UnicodeDammit

PASTEBIN_RAW_PREFIX = "http://pastebin.com/raw.php?i="
FLASHVARS_FORMAT = "initCallback=onPlayerLoad&channel={channel}&" \
                   "auto_play=false&start_volume=25&" \
                   "archive_id={archive_id}"
TEMPLATE_FILE = "template.html"

def get_message(line, regex, timestamp_format):
    try:
        match = regex.match(line)
        stamp = datetime.strptime(match.group("timestamp"), timestamp_format)

        return stamp, match.group("username"), \
               match.group("message"), match.group("service")
    except AttributeError:
        # Regex didn't match
        return None

def format_message(message, message_format, service_format):
    if message[1] is not None:
        return message_format.format(username=message[1], message=message[2])
    else:
        return service_format.format(service=message[3])

# Extract config file name from command line
# (or default to 'config.ini')
parser = argparse.ArgumentParser(description='Create players for past '
                                             'DF Game Club sessions')
parser.add_argument('config', nargs='?', default='config.ini',
                    help='configuration file with past session data')
namespace = parser.parse_args()

# Read configuration file
conf = configparser.ConfigParser(interpolation=None)
conf.read(namespace.config)

for section in conf.sections():
    pastebin_url = PASTEBIN_RAW_PREFIX + \
                    urlparse(conf[section]["pastebin_url"]).path.strip('/')
    log = UnicodeDammit(urlopen(pastebin_url).read()).unicode_markup
    log = log.replace('\r', '').split('\n')

    regex = re.compile(conf[section]['regex'])
    timestamp_format = conf[section]['timestamp_format']
    video_timestamp = conf[section]['video_timestamp']

    twitch_url = urlparse(conf[section]['twitch_url'])\
        .path.strip('/').split('/')
    channel, archive_id = twitch_url[0], twitch_url[2]

    ignore_lines = [
        int(num) for num in [
            item for item in
                conf[section]['ignore_lines'].replace(' ','').split(',')
            if item != ''
        ]
    ]

    message_format = conf[section]['message_format']
    service_format = conf[section]['service_format']

    with open(section + ".json", mode='w') as g:
        last_msg = get_message(log[0], regex, timestamp_format)
        messages = []

        video_delay = (datetime.strptime(video_timestamp, timestamp_format) -
                       last_msg[0]).total_seconds() * 1000

        for line_num, line in enumerate(log):
            # Skip line if flagged
            if line_num + 1 in ignore_lines:
                continue

            temp = get_message(line, regex, timestamp_format)

            if temp is None:
                print("error: regular expression didn't match line.")
                print("section:  {}".format(section))
                print("line num: {}".format(line_num + 1))
                print("line:     {}".format(line))
                print()
                sys.exit()

            messages.append({
                "message":format_message(temp, message_format, service_format),
                "delay"  :(temp[0] - last_msg[0]).total_seconds() * 1000
            })

            last_msg = temp

        g.write(json.dumps([video_delay, messages], separators=(',', ':')))

    with open(TEMPLATE_FILE, mode='r') as template:
        soup = BeautifulSoup(template.read())
        soup.body.find('article', id='main').object\
            .find('param', attrs={"name":"flashvars"})["value"] = \
            FLASHVARS_FORMAT.format(channel=channel, archive_id=archive_id)
        with open(section + ".html", mode='w') as g:
            g.write(str(soup))
