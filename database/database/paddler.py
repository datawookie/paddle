from .base import *
from .person import *
from .club import *
from .entry import *


class Paddler(Base):
    __tablename__ = "paddler"

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey(Person.id), index=True)
    club_id = Column(String(3), ForeignKey(Club.id), index=True)
    entry_id = Column(Integer, ForeignKey(Entry.id), index=True)

    person = relationship("Person", backref="paddlers", lazy="joined")
    club = relationship("Club", backref="paddlers", lazy="joined")
    entry = relationship(Entry, backref="paddlers", lazy="joined")

    def __repr__(self):
        club = f"'{self.club.id}'" if self.club else "NONE"
        return f"Paddler(name='{self.person.name}', club={club})"
