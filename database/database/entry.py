import enum
import datetime
from .base import *
from .race import *
from .team import *
from .category import *
from .series import *
from .team import *


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
    race_number = Column(Integer)
    online = Column(Boolean)
    series = Column(Boolean)
    series_id = Column(Integer, ForeignKey(Series.id), index=True)

    time_start = Column(String)
    time_finish = Column(String)
    retired = Column(Boolean)
    disqualified = Column(Boolean)

    category = relationship(Category, backref="entries", lazy="joined")
    race = relationship(Race, backref="entries", lazy="joined")

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
