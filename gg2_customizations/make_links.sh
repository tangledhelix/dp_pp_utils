#!/bin/bash
#
# Set up ~/Documents/GGprefs with links here

# List of files to link
FILES="abbr.json html_header.txt misc_checks.json dict_la_user.txt dict_it_user.txt"

GG_DIR="${HOME}/Documents/GGprefs"
if [[ ! -d "${GG_DIR}" ]]; then
    echo "No such directory: ${GG_DIR}"
    exit 1
fi

MY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for f in $FILES; do
    if [[ ! -f "${MY_DIR}/${f}" ]]; then
        echo "** SKIP ${f} - no source file found"
        continue
    fi

    if [[ -L "${GG_DIR}/${f}" ]]; then
        printf "Found ${f} link; replacing... "
        rm -f "${GG_DIR}/${f}"
        ln -s "${MY_DIR}/${f}" "${GG_DIR}/${f}"
        echo "done."
    elif [[ -f "${GG_DIR}/${f}" ]]; then
        echo "** SKIP ${f} - found non-symlink in target dir!"
        continue
    else
        printf "No ${f} link found; creating one... "
        ln -s "${MY_DIR}/${f}" "${GG_DIR}/${f}"
        echo "done."
    fi
done
