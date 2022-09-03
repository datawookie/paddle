from .base import *


class Race(Base):
    __tablename__ = "race"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    day = Column(Date)

    # TODO: Add other information from configuration file. For example:
    #
    # start_time_min
    # start_time_max
    # finish_time_min
    # finish_time_max
    # elapsed_time_min (redundant?)
    # elapsed_time_max (redundant?)

    def __repr__(self):
        return "Race('%s', '%s')" % (self.name, self.day)
