from .base import *


class Race(Base):
    __tablename__ = "race"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    day = Column(Date)

    def __repr__(self):
        return "Race('%s', '%s')" % (self.name, self.day)
