#!/usr/bin/env python3

"""
Find and display long lines in an ebook text file.
"""

# Lines should not be longer than this
MAX_LEN = 72

import sys

if len(sys.argv) < 2:
    sys.exit("Missing argument: filename")

lineno = 0

with open(sys.argv[1], "r") as f:
    for line in f:
        lineno += 1
        line = line.rstrip()
        linelen = len(line)
        if linelen > MAX_LEN:
            print(f"{lineno} ({linelen}): {line}")
