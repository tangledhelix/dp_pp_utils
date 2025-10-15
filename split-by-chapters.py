#!/usr/bin/env python3
#
# Load an HTML file and split, by chapter, into multiple output files.  Why
# split? In order to load a larger book into a custom GPT, it can help avoid
# exceeding the maximum available context window.
#
# You can't upload more than 20 files to a custom GPT. Don't split *every*
# chapter; let the user control how many chapters are in a chunk.
#

chapters_per_chunk = 1

import os
import sys
import re

if len(sys.argv) < 2:
    print("Error: missing argument: input_filename")
    print(f"Usage: {sys.argv[0]} <input_filename> [<chapters_per_file>]")
    print("    (chapters_per_file defaults to 1)")
    sys.exit(1)

if len(sys.argv) > 2:
    chapters_per_chunk = int(sys.argv[2])

if not os.path.exists(sys.argv[1]):
    print("file not found:", sys.argv[1])
    sys.exit(1)

# incrementer for output filenames
foutcount = 1
chapcount = 0

(fname, fnext) = os.path.splitext(sys.argv[1])
bname = os.path.basename(fname)

def foutopen(fh=None):
    if fh:
        fh.close()
    return open(f"{bname}{foutcount:03d}{fnext}", "w")

chapsep = r'<div class="chapter"'

with open(sys.argv[1], "r") as fr:
    fout = foutopen()

    for line in fr.readlines():
        if re.search(chapsep, line):
            chapcount += 1
            if chapcount >= chapters_per_chunk:
                foutcount += 1
                fout = foutopen(fout)
                chapcount = 0
        fout.write(line)

    fout.close()
