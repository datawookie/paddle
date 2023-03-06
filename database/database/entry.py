import enum
import hashlib
import logging
from functools import cached_property

import datetime
from collections import OrderedDict
from .base import *
from .race import Race
from .team import Team
from .category import Category
from .series import Series


class BoatType(enum.Enum):
    K1 = 1
    K2 = 2
    C = 3


boat_type = Enum(BoatType)


class Entry(Base):
    __tablename__ = "entry"

    id = Column(Integer, primary_key=True)
    race_id = Column(Integer, ForeignKey(Race.id), index=True)
    category_id = Column(Integer, ForeignKey(Category.id), index=True)
    boat_type = Column(boat_type, index=True)
    entry_number = Column(Integer)
    series_id = Column(Integer, ForeignKey(Series.id), index=True)

    time_start = Column(String)
    time_finish = Column(String)
    time_adjustment = Column(Integer)
    registered = Column(Boolean, default=False, nullable=False)
    retired = Column(Boolean, default=False, nullable=False)
    scratched = Column(Boolean, default=False, nullable=False)
    disqualified = Column(Boolean, default=False, nullable=False)
    note = Column(Text)

    category = relationship(Category, backref="entries", lazy="joined")
    race = relationship(Race, backref="entries", lazy="joined")
    race_number = relationship("Number", secondary="number_entry", uselist=False)
    # Don't use a backref here so that can order by paddler ID.
    crews = relationship("Crew", lazy="joined", order_by="Crew.paddler_id")

    @property
    def division(self):
        if self.crews:
            # The division assigned to the boat is the minimum of the divisions of the paddlers.
            divisions = [crew.paddler.division for crew in self.crews]
            divisions = [division for division in divisions if division is not None]
            if divisions:
                return min(divisions)

        return None

    def __repr__(self):
        return "Entry(id=%d)" % (self.id,)

    def __str__(self):
        names = [str(crew) for crew in self.crews]
        return " / ".join(names)

    @cached_property
    def crew_hash(self):
        paddlers = [str(crew.paddler.id) for crew in self.crews]
        paddlers = ",".join(paddlers)
        return hashlib.md5(paddlers.encode("utf-8")).hexdigest()

    @property
    def time(self):
        if self.time_start and self.time_finish:
            time_start = datetime.datetime.strptime(self.time_start, "%H:%M:%S")
            time_finish = datetime.datetime.strptime(self.time_finish, "%H:%M:%S")
            return (
                time_finish
                - time_start
                + datetime.timedelta(seconds=(self.time_adjustment or 0))
            )
        else:
            return None

    @property
    def team(self):
        # An entry is only considered a team entry if all of the paddlers in the boat are on the same team.
        #
        # K1:
        #
        # - [None]                      paddler not in a team
        # - ["Warriors"]                paddler in a team
        #
        # K2:
        #
        # - [None, None]                neither paddler in a team
        # - ["Warriors", None]          paddler in a team + paddler not in a team
        # - [None, "Warriors"]          paddler in a team + paddler not in a team
        # - ["Warriors", "Warriors"]    both paddlers in same taem
        # - ["Warriors", "Chiefs"]      paddlers in different teams
        #
        teams = [crew.team for crew in self.crews]
        teams = list(set(teams))
        if len(teams) == 1:
            return teams[0]
        else:
            return None

    @property
    def complete(self):
        # An entry is considered complete if:
        #
        # - both paddlers have names.
        #
        return not any([crew.paddler.name == "" for crew in self.crews])

    @property
    def crew_complete(self):
        return len(self.crews) >= self.category.crew_count

    @property
    def services(self):
        # An entry is only considered a services entry if all of the paddlers in the boat in the services.
        services = [crew.services for crew in self.crews]
        return all(services)

    @property
    def started(self):
        return self.time_start is not None

    @property
    def finished(self):
        return self.time_start is not None and (
            self.time_finish is not None or self.retired or self.disqualified
        )

    @property
    def clubs(self):
        clubs = [crew.club.id for crew in self.crews]
        return "/".join(clubs)


class EntrySet:
    def __init__(self, entries):
        # Get paddler names for all entries.
        names = [tuple(crew.paddler.name for crew in entry.crews) for entry in entries]
        # There should only be one set of paddler names for all entries in set.
        names = list(set(names))
        assert len(names) == 1
        names = names[0]
        # Concatenate names.
        self.name = " / ".join(names)

        # Total time for all entries in set.
        self.time = sum([entry.time for entry in entries], datetime.timedelta())

    def __repr__(self):
        return f"EntrySet(name='{self.name}', time='{self.time}')"


def entries_get_categories(entries):
    # Get all categories from entries.
    #
    categories = set()
    #
    for entry in entries:
        categories.add((entry.category.id, entry.category.label))

    # Sort categories by ID.
    #
    categories = OrderedDict(sorted(categories, key=lambda t: t[0]))

    # Use labels as keys.
    #
    categories = {label: [] for id, label in categories.items()}

    # Group results into categories.
    #
    for entry in entries:
        categories[entry.category.label].append(entry)

    return categories
