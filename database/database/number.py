from .base import *
from .race import Race
from .entry import Entry

MAX_NUMBER = 599


class Number(Base):
    __tablename__ = "number"

    id = Column(Integer, primary_key=True)
    lost = Column(Boolean)

    def __repr__(self):
        return "Number(%d, lost=%s)" % (self.id, self.lost)

    def __str__(self):
        return str(self.id)


class NumberAllocation(Base):
    __tablename__ = "number_entry"

    id = Column(Integer, primary_key=True)
    number_id = Column(Integer, ForeignKey(Number.id), nullable=False)
    entry_id = Column(Integer, ForeignKey(Entry.id), nullable=True)
