#!/usr/bin/env python3

import getopt, sys
from os.path import basename

import database as db
from database.logging import logger

# # ---------------------------------------------------------------------------------------------------------------------

OPTIONS_LONG = [
    "help",
    "debug",
    "dry-run",
    "create-tables",
]


HELP_STRING = (
    "Usage: %s <option>" % (basename(sys.argv[0]))
    + "\n\nwhere <option> is one of\n\n"
    + "\n".join(["\t--" + option for option in OPTIONS_LONG])
)

if __name__ == "__main__":
    session = db.Session()

    DEBUG = False
    DRYRUN = False

    try:
        arguments, values = getopt.getopt(sys.argv[1:], "", OPTIONS_LONG)
    except getopt.error as err:
        print(str(err))
        sys.exit(2)

    for argument, value in arguments:
        if argument == "--help":
            print(HELP_STRING)
            sys.exit(0)
        elif argument == "--debug":
            DEBUG = True
        elif argument == "--dry-run":
            DRYRUN = True

    for argument, value in arguments:
        if argument in ("--create-tables"):
            logger.info("Creating tables...")
            db.Base.metadata.create_all(db.engine)
            logger.info("Done.")
