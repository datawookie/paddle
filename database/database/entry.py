from .base import *
from .race import *
from .category import *
from .series import *
from .team import *
import enum


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
    team_id = Column(Integer, ForeignKey(Team.id), index=True)
    boat_type = Column(boat_type, index=True)
    entry_number = Column(Integer)
    online = Column(Boolean)
    series = Column(Boolean)
    series_id = Column(Integer, ForeignKey(Series.id), index=True)

    time_start = Column(String)
    time_finish = Column(String)

    @property
    def division(self):
        # The division assigned to the boat is the minimum of the divisions of the paddlers.
        return min([seat.paddler.division for seat in self.seats])

    def __repr__(self):
        return "Entry(%d)" % (self.entry_number)

    def __str__(self):
        names = [str(seat) for seat in self.seats]
        return " / ".join(names)
