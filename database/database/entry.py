from .base import *
from .race import *
from .category import *
from .series import *
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
    series_id = Column(Integer, ForeignKey(Series.id), index=True)
    boat_type = Column(boat_type, index=True)
    entry_number = Column(Integer)

    def __repr__(self):
        return "Entry(%d)" % (self.entry_number)
