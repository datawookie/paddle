import enum
import datetime
from .base import *
from .race import *
from .team import *
from .category import *
from .series import *


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
    online = Column(Boolean)
    series = Column(Boolean)
    series_id = Column(Integer, ForeignKey(Series.id), index=True)

    time_start = Column(String)
    time_finish = Column(String)
    time_adjustment = Column(Integer)
    registered = Column(Boolean, default=False, nullable=False)
    retired = Column(Boolean, default=False, nullable=False)
    disqualified = Column(Boolean, default=False, nullable=False)
    note = Column(Text)

    category = relationship(Category, backref="entries", lazy="joined")
    race = relationship(Race, backref="entries", lazy="joined")
    race_number = relationship("Number", secondary="number_entry", uselist=False)

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
        return f"Entry(id={self.id}, category_id={self.category_id}, entry_number={self.entry_number})"

    def __str__(self):
        names = [str(crew) for crew in self.crews]
        return " / ".join(names)

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


def entries_get_categories(entries):
    categories = {}
    #
    # Group results into categories.
    #
    for entry in entries:
        try:
            categories[entry.category.label]
        except KeyError:
            categories[entry.category.label] = []

        categories[entry.category.label].append(entry)

    return categories
