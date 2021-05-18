#!/usr/bin/expect -f

set timeout -1
spawn python bootstrap.py --application-choice=browser --no-interactive --vcs=git
expect "Destination directory for Git clone (leave empty to not clone)"
send -- "\r"
expect eof

