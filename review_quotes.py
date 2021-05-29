#!/usr/bin/env python3
#
# Review an HTML file looking for straight & curly quotes. First, strip
# the HTML tags, since straight double quotes will be in tag attributes.
# Straight single quotes might also appear as comments in CSS.
#
# Report on what kinds of quotes were found. At the end, write the cleaned
# file to disk to make it easier to locate any errant quotes, if any
# were seen.

import sys

from bs4 import BeautifulSoup

DEBUG = True

if len(sys.argv) < 2:
    print("Error: missing filename")
    sys.exit(1)

fname = sys.argv[1]
fname_out = f"{fname}-stripped.txt"

seen_straight = False


def debug(msg):
    if DEBUG:
        print(msg)


with open(fname, "r") as f:
    # read entire html file into a string
    html_string = f.read()

    # strip all the tags and give me back only text
    clean_text = " ".join(BeautifulSoup(html_string, "html.parser").stripped_strings)

    # look for each quote type in the result
    if "'" in clean_text:
        print("WARN: straight single quote(s) found")
        seen_straight = True
    if '"' in clean_text:
        print("WARN: straight double quote(s) found")
        seen_straight = True

    if '“' in clean_text:
        debug("OK: left curly double quote(s) found")
    if '”' in clean_text:
        debug("OK: right curly double quote(s) found")

    if '‘' in clean_text:
        debug("OK: left curly single quote(s) found")
    if '’' in clean_text:
        debug("OK: right curly single quote(s) found")

    if seen_straight:
        print(f"--- Writing cleaned text to {fname_out} ...")
        with open(fname_out, "w") as f2:
            f2.write(clean_text)
