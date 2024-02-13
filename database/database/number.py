from .base import *
from .category import Category
from .entry import Entry
from .race import Race

MAX_NUMBER = 599


class Number(Base):
    __tablename__ = "number"

    id = Column(Integer, primary_key=True)
    lost = Column(Boolean)

    def __repr__(self):
        return "Number(%d, lost=%s)" % (self.id, self.lost)

    def __str__(self):
        return str(self.id)

    def __int__(self):
        return int(self.id)


class NumberEntry(Base):
    __tablename__ = "number_entry"

    id = Column(Integer, primary_key=True)
    number_id = Column(Integer, ForeignKey(Number.id), nullable=False)
    entry_id = Column(Integer, ForeignKey(Entry.id), nullable=True)


class RaceNumber(Base):
    __tablename__ = "race_number"
    __table_args__ = (
        UniqueConstraint("race_id", "category_id", name="uq_race_category"),
    )

    id = Column(Integer, primary_key=True)
    race_id = Column(Integer, ForeignKey(Race.id), nullable=True)
    category_id = Column(Integer, ForeignKey(Category.id), nullable=True)
    min_number_id = Column(Integer, ForeignKey(Number.id), nullable=False)
    max_number_id = Column(Integer, ForeignKey(Number.id), nullable=False)
