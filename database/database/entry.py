import datetime
import enum
import hashlib
import logging
from collections import OrderedDict
from functools import cached_property

from .base import *
from .category import Category
from .race import Race
from .series import Series
from .team import Team


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
        names = sorted([str(crew) for crew in self.crews])
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
        # - ["Warriors"]                paddler in a team ✅
        #
        # K2:
        #
        # - [None, None]                neither paddler in a team
        # - ["Warriors", None]          paddler in a team + paddler not in a team
        # - [None, "Warriors"]          paddler in a team + paddler not in a team
        # - ["Warriors", "Warriors"]    both paddlers in same team ✅
        # - ["Warriors", "Chiefs"]      paddlers in different teams
        #
        # * Each paddler may be associated with zero or more teams.
        # * Iterate over these teams and see if any of them relate to this race.
        #
        teams = [
            team
            for crew in self.crews
            for team in crew.paddler.teams
            if self.race.series_id == team.series_id
        ]
        #
        unique = list(set(teams))
        #
        if len(unique) == 1 and len(teams) == len(self.crews):
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
        return len(services) > 0 and all(services)

    @property
    def is_started(self):
        return self.time_start is not None

    @property
    def is_finished(self):
        return self.time_start is not None and (
            self.time_finish is not None or self.retired or self.disqualified
        )

    @property
    def clubs(self):
        clubs = [crew.club for crew in self.crews]
        clubs = [club.code if club.code else "—" for club in clubs]
        return "/".join(clubs)

    @property
    def age_groups(self):
        return [
            crew.paddler.age_group.label if crew.paddler.age_group else None
            for crew in self.crews
        ]

    @property
    def genders(self):
        return [crew.paddler.gender for crew in self.crews]

    @property
    def is_junior(self):
        return all(age_group == "Junior" for age_group in self.age_groups)

    @property
    def is_senior(self):
        return all(age_group == "Senior" for age_group in self.age_groups)

    @property
    def is_veteran(self):
        return all(age_group == "Veteran" for age_group in self.age_groups)

    @property
    def is_master(self):
        return all(age_group == "Master" for age_group in self.age_groups)

    @property
    def is_male(self):
        return all(gender == "M" for gender in self.genders)

    @property
    def is_female(self):
        return all(gender == "F" for gender in self.genders)

    @property
    def is_mixed(self):
        return len(self.genders) == 2 and "M" in self.genders and "F" in self.genders


class EntrySet:
    def __init__(self, entries):
        names = {}

        for entry in entries:
            for crew in entry.crews:
                try:
                    names[crew.paddler.name]
                except KeyError:
                    names[crew.paddler.name] = {"club": [], "gender": [], "age": []}

                if crew.club:
                    names[crew.paddler.name]["club"].append(crew.club.name)
                if crew.paddler.age_group:
                    names[crew.paddler.name]["age"].append(
                        crew.paddler.age_group.abbreviation
                    )
                if crew.paddler.gender:
                    names[crew.paddler.name]["gender"].append(crew.paddler.gender)

        for _, data in names.items():
            # If a paddler is linked to multiple clubs then they are joined with "+".
            data["club"] = "+".join(set(data["club"]))
            # Need a single value for gender and age. Probably don't need to join()!
            data["gender"] = "+".join(set(data["gender"]))
            data["age"] = "+".join(set(data["age"]))

        self.name = " / ".join(names.keys())
        self.club = " / ".join([name["club"] for name in names.values()])
        self.gender = " / ".join([name["gender"] for name in names.values()])
        self.age = " / ".join([name["age"] for name in names.values()])

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


def entries_get_clubs(entries):
    # Get all categories from entries.
    #
    clubs = set()
    #
    for entry in entries:
        for crew in entry.crews:
            if crew.club:
                clubs.add((crew.club.id, crew.club.name))

    # Sort clubs by name.
    #
    clubs = OrderedDict(sorted(clubs, key=lambda t: t[1]))

    # Use names as keys.
    #
    clubs = {name: set() for id, name in clubs.items()}

    # Group results into categories.
    #
    for entry in entries:
        for crew in entry.crews:
            if crew.club:
                clubs[crew.club.name].add(entry)

    # Convert from set to list.
    #
    for key in clubs:
        clubs[key] = list(clubs[key])

    return clubs
