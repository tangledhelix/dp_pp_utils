#!/usr/bin/env python3
#
# This script is historical - DP has converted to a UTF-8 workflow,
# so converting from Latin-1 to UTF-8 is no longer necessary.
#
# -------------------------------------------------------------------
#
# Convert a Latin-1 file to UTF-8
#
# This same process happens in make_project.py, so you won't need this
# often, but it's here if needed.

import sys

if len(sys.argv) < 2:
    print('Error: Missing argument.')
    print('Usage: {} <input-file>'.format(sys.argv[0]))
    sys.exit(1)

input_file = sys.argv[1]
if not input_file.endswith('.txt'):
    print('Error: Filename must end with ".txt"')
    sys.exit(1)

output_file = '{}-utf8.txt'.format(input_file[:-4])

try:
    with open(input_file, encoding='latin-1') as file:
        contents = file.read()
except FileNotFoundError:
    print('Error: {}: file not found'.format(input_file))
    sys.exit(1)

try:
    with open(output_file, 'x', encoding='utf-8') as file:
        file.write(contents)
except FileExistsError:
    print('Error: {} already exists!'.format(output_file))
    sys.exit(1)

print('created {}'.format(output_file))
