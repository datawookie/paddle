import logging
import re
from datetime import datetime

from .base import *
from .series import Series


class Race(Base):
    __tablename__ = "race"
    __table_args__ = (UniqueConstraint("name", "date", name="uq_race_name_date"),)

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    series_id = Column(Integer, ForeignKey(Series.id), index=True)
    time_min_start = Column(String)
    time_max_start = Column(String)
    time_min_finish = Column(String)
    time_max_finish = Column(String)
    time_adjustment = Column(Integer)

    series = relationship(Series, backref="races", lazy="joined")

    # TODO: Add other information from configuration file. For example:
    #
    # start_time_min
    # start_time_max
    # finish_time_min
    # finish_time_max
    # elapsed_time_min (redundant?)
    # elapsed_time_max (redundant?)

    def __repr__(self):
        return "Race('%s', '%s')" % (self.name, self.date)

    def __str__(self):
        return "%s (%s)" % (self.name, self.date)

    @property
    def slug(self):
        return re.sub("[^a-zA-Z0-9]+", "-", self.name).lower()

    @property
    def past(self):
        return datetime.today().date() >= self.date

    @property
    def future(self):
        return not self.past
