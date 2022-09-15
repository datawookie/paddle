import enum
import datetime
from .base import *
from .race import *
from .team import *
from .category import *
from .series import *
from .team import *
from .number import *


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
    number_id = Column(Integer, ForeignKey(Number.id), index=True)
    online = Column(Boolean)
    series = Column(Boolean)
    series_id = Column(Integer, ForeignKey(Series.id), index=True)

    time_start = Column(String)
    time_finish = Column(String)
    retired = Column(Boolean)
    disqualified = Column(Boolean)

    category = relationship(Category, backref="entries", lazy="joined")
    race = relationship(Race, backref="entries", lazy="joined")
    race_number = relationship(Number, backref="entries")

    @property
    def division(self):
        # The division assigned to the boat is the minimum of the divisions of the paddlers.
        return min([seat.paddler.division for seat in self.seats])

    def __repr__(self):
        return "Entry(%d)" % (self.entry_number)

    def __str__(self):
        names = [str(seat) for seat in self.seats]
        return " / ".join(names)

    @property
    def time(self):
        if self.time_start and self.time_finish:
            time_start = datetime.datetime.strptime(self.time_start, "%H:%M:%S")
            time_finish = datetime.datetime.strptime(self.time_finish, "%H:%M:%S")
            return time_finish - time_start
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
        teams = [seat.team for seat in self.seats]
        teams = list(set(teams))
        if len(teams) == 1:
            return teams[0]
        else:
            return None

    @property
    def services(self):
        # An entry is only considered a services entry if all of the paddlers in the boat in the services.
        services = [seat.services for seat in self.seats]
        return all(services)
