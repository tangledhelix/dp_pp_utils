#!/bin/zsh

# Do a quick scan of projects in the current directory for any with
# a dirty git status.

for p in *(/)
do
    o=""
    cd $p
    o=$(git status --porcelain)
    if [ -n "${o##+([[:space:]])}" ]; then
        echo "## $p"
        echo $o
        echo
    fi
    cd ..
done
