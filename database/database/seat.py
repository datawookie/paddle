from .base import *
from .paddler import *
from .club import *
from .entry import *


class Seat(Base):
    __tablename__ = "seat"

    id = Column(Integer, primary_key=True)
    paddler_id = Column(Integer, ForeignKey(Paddler.id), index=True)
    club_id = Column(String(3), ForeignKey(Club.id), index=True)
    entry_id = Column(Integer, ForeignKey(Entry.id), index=True)
    paid = Column(Numeric)

    paddler = relationship(Paddler, backref="seats", lazy="joined")
    club = relationship("Club", backref="seats", lazy="joined")
    entry = relationship(Entry, backref="seats", lazy="joined")

    def __repr__(self):
        club = f"'{self.club.id}'" if self.club else "NONE"
        return f"Seat(name='{self.paddler.name}', club={club})"

    def __str__(self):
        club = f" ({self.club.id})" if self.club else ""
        return f"{self.paddler.name}{club}"
