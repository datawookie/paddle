#!/usr/bin/env python3

import getopt
import sys
from sqlite3 import IntegrityError
import csv
from os.path import basename

import database as db
from database.logging import logger

# ---------------------------------------------------------------------------------------------------------------------

OPTIONS_LONG = [
    "help",
    "debug",
    "dry-run",
    "drop-tables",
    "create-tables",
]


HELP_STRING = (
    "Usage: %s <option>" % (basename(sys.argv[0]))
    + "\n\nwhere <option> is one of\n\n"
    + "\n".join(["\t--" + option for option in OPTIONS_LONG])
)

# ---------------------------------------------------------------------------------------------------------------------

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
        if argument in ("--drop-tables"):
            logger.info("Dropping tables...")
            db.Base.metadata.drop_all(db.engine)
            logger.info("Done.")
        if argument in ("--create-tables"):
            logger.info("Creating tables...")
            db.Base.metadata.create_all(db.engine)
            logger.info("Done.")

            logger.info("Populate club table...")
            with open("club-list.csv", newline="") as file:
                reader = csv.reader(file, delimiter=",")
                # Skip header record.
                next(reader)
                for row in reader:
                    club = db.Club(id=row[0], name=row[1])
                    session.add(club)
                    logger.debug("  - " + str(club))
            try:
                session.commit()
            except db.IntegrityError:
                session.rollback()
                logger.warning("Table already populated.")
            else:
                logger.info("Done.")

            logger.info("Populate category table...")
            for category in db.CATEGORY_LIST:
                category = db.Category(label=category)
                session.add(category)
                logger.debug("  - " + str(category))
            try:
                session.commit()
            except db.IntegrityError:
                session.rollback()
                logger.warning("Table already populated.")
            logger.info("Done.")

            logger.info("Populate number table...")
            for number in range(db.MAX_NUMBER):
                number = db.Number(id=number + 1)
                session.add(number)
            try:
                session.commit()
            except db.IntegrityError:
                session.rollback()
                logger.warning("Table already populated.")
            logger.info("Done.")
