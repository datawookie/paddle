from .base import *
from .series import Series


class Race(Base):
    __tablename__ = "race"
    __table_args__ = (UniqueConstraint("name", "date", name="uq_race_name_date"),)

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    series_id = Column(Integer, ForeignKey(Series.id), index=True)

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
