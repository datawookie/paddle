from .base import *
from .paddler import *
from .club import *
from .entry import *


class Crew(Base):
    __tablename__ = "crew"

    id = Column(Integer, primary_key=True)
    paddler_id = Column(Integer, ForeignKey(Paddler.id), index=True)
    club_id = Column(String(3), ForeignKey(Club.id), index=True)
    entry_id = Column(Integer, ForeignKey(Entry.id), index=True)
    team_id = Column(Integer, ForeignKey(Team.id), index=True)
    services = Column(Boolean, server_default=expression.false())
    due = Column(Numeric)
    paid = Column(Numeric)

    team = relationship(Team, backref="crews", lazy="joined")
    paddler = relationship(Paddler, backref="crews", lazy="joined")
    club = relationship("Club", backref="crews", lazy="joined")
    entry = relationship(Entry, backref="crews", lazy="joined")

    def __repr__(self):
        club = f"'{self.club.id}'" if self.club else "None"
        return f"Crew(name='{self.paddler.name}', club_id={club})"

    def __str__(self):
        club = f" ({self.club.code})" if self.club else ""
        return f"{self.paddler.name}{club}"
