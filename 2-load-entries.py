import sys
import json

import database as db

session = db.Session()


def load_entries(entries):
    for entry in entries:
        print(entry)

        person = db.Person(
            first=entry["first"],
            last=entry["last"],
            division=entry["division"],
        )
        session.add(person)

        club = session.query(db.Club).get(entry["club"])

        person.paddlers.append(db.Paddler(club=club))

    session.commit()


if __name__ == "__main__":
    PATH = sys.argv[1]
    with open(PATH, "rt") as file:
        entries = file.read()

    load_entries(json.loads(entries))
