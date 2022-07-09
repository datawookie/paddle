from .base import *
from .person import *
from .boat import *


class Paddler(Base):
    __tablename__ = "paddler"

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey(Person.id), index=True)
    club_id = Column(String(3), ForeignKey(Club.id), index=True)
    boat_id = Column(Integer, ForeignKey(Boat.id), index=True)

    person = relationship("Person", backref="paddlers")
    club = relationship("Club", backref="paddlers")
    boat = relationship("Boat", backref="paddlers")
