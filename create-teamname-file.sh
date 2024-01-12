#!/bin/bash

# Generate TEAMNAME.TXT file required by old system.

sqlite3 paddle.db "select name from team;" | sed -E 's/(.*) \((.*)\)/\2,\1/' | sort
