from .base import *


class Member(Base):
    __tablename__ = "member"

    id = Column(Integer, primary_key=True)
    first = Column(String)
    middle = Column(String)
    last = Column(String)

    time_trial_results = relationship("TimeTrialResult", back_populates="member")

    @property
    def name(self):
        name = [self.first, self.last]
        name = list(filter(lambda item: item is not None, name))
        name = " ".join(name)
        name = name.strip()
        return name
