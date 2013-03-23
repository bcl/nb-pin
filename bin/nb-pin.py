#!/usr/bin/env python
"""
    Newsbeuter pinboard.in bookmarking

    Copyright 2013 by Brian C. Lane

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
import sys
import os
import requests
import argparse
import stat

debug = False

class Pinboard(object):
    API = "https://api.pinboard.in/v1/"

    def __init__(self, url, title, desc, auth_token, tags=None, replace=False, shared=False, toread=False):
        """ Bookmark a URL using pinboard.in

            :param url: The website's URL
            :type url: string
            :param title: Title of the URL
            :type title: string
            :param desc: Description of the url
            :type desc: string
            :param auth_token: pinboard.in auth token
            :type auth_token: string
            :param tags: optional tags (no , or spaces)
            :type tags: list
            :param replace: Replace existing URL if True (default: False)
            :type replace: bool
            :param shared: Share url publicly if True (default: False)
            :type shared: bool
            :param toread: Mark it to read later if True (default: False)
            :type toread: bool
            :return: If there was an error it will print a 1 line error
            :rtype: string

            See https://pinboard.in/api/ for API details
        """
        payload = {}
        payload["url"] = url
        payload["description"] = title
        payload["auth_token"] = auth_token
        if desc:
            payload["extended"] = desc
        if tags:
            payload["tags"] = " ".join([t.translate(None, " ,") for t in tags if t])
        payload["replace"] = "yes" if replace else "no"
        payload["shared"] = "yes" if shared else "no"
        payload["toread"] = "yes" if toread else "no"

        if debug:
            print(payload)

        try:
            r = requests.get(self.API+"posts/add", params=payload)
            if r.status_code != 200:
                print("ERROR: Status code %s for %s" % (r.status_code, payload))
        except Exception as e:
            print("ERROR for %s: %s" % (payload, e))


def setup_argparse():
    """ Handle setup of the argparse options
    """
    parser = argparse.ArgumentParser(description="Pinboard Newsbeuter Bookmarks")
    parser.add_argument("-c", "--config", help="Path to config file", type=os.path.expanduser, default="~/.pinboard-auth")
    parser.add_argument("-t", "--tag", help="tag, multiple allowed", action="append") 
    parser.add_argument("-r", "--replace", help="Replace an existing URL", action="store_true")
    parser.add_argument("-s", "--shared", help="Share the URL publicly", action="store_true")
    parser.add_argument("-l", "--later", help="Read later", action="store_true")
    parser.add_argument("-d", "--debug", help="Turn on debugging output", action="store_true")
    parser.add_argument("url", help="URL to pin")
    parser.add_argument("title", help="Title of the URL")
    parser.add_argument("description", help="Description of url", nargs="?", default="")

    return parser


def get_auth_token(config_file):
    """ Get the pinboard.in auth token from the configuration file.

        Check permissions on the file and raise an error if it is
        accessable to anyone other than the user.

        File should have a line like this:
        auth_token=USER:BUNCHOFHEXCHARS

        You can obtain your token from the password page of your pinboard.in account

        :param config_file: Full path to the file, supports ~ expansion
        :type config_file: string
        :raises: Exception
        :returns: nothing
    """
    file_path = os.path.expanduser(config_file)
    # Check config mode, refuse to run if they aren't 0600
    info = os.stat(file_path)
    if info.st_mode & (stat.S_IRWXG | stat.S_IRWXO):
        raise Exception("ERROR: %s should not be accessable to others" % config_file)

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            token, sep, value = line.partition("=")
            if token == "auth_token":
                return value
    return ""


def main():
    """
    Main code goes here
    """
    parser = setup_argparse()
    args = parser.parse_args()
    debug = args.debug

    if debug:
        print(args)

    # Check config mode, refuse to run if it isn't 0600
    if not os.path.exists(args.config):
        print("ERROR: Config file %s doesn't exist" % args.config)
        sys.exit(1)

    try:
        auth_token = get_auth_token(args.config)
    except Exception as e:
        print(str(e))
        sys.exit(1)

    Pinboard(args.url, args.title, args.description, auth_token,
             args.tag, args.replace, args.shared, args.later)

if __name__ == '__main__':
    main()


