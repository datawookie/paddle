from .base import *
from .member import *


class TimeTrial(Base):
    __tablename__ = "time_trial"

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    distance = Column(Numeric)

    time_trial_results = relationship("TimeTrialResult", back_populates="time_trial")


class TimeTrialResult(Base):
    __tablename__ = "time_trial_result"

    id = Column(Integer, primary_key=True)
    time_trial_id = Column(Integer, ForeignKey(TimeTrial.id), index=True)
    member_id = Column(Integer, ForeignKey(Member.id), index=True)
    time = Column(String)

    time_trial = relationship(TimeTrial, back_populates="time_trial_results")
    member = relationship(Member, back_populates="time_trial_results")

    def __str__(self):
        return str(self.time)
