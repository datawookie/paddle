from .base import *
from .club import *
from .entry import *
from .paddler import *


class Crew(Base):
    __tablename__ = "crew"

    id = Column(Integer, primary_key=True)
    paddler_id = Column(Integer, ForeignKey(Paddler.id), index=True)
    club_id = Column(String(3), ForeignKey(Club.id), index=True)
    entry_id = Column(Integer, ForeignKey(Entry.id), index=True)
    services = Column(Boolean, server_default=expression.false())
    due = Column(Numeric)
    paid = Column(Numeric)

    paddler = relationship(Paddler, backref="crews", lazy="joined")
    club = relationship("Club", backref="crews", lazy="joined")
    entry = relationship(Entry, lazy="joined", overlaps="crews")

    def __repr__(self):
        club_id = f"{self.club.id}" if self.club else "None"
        entry_id = f"{self.entry.id}" if self.entry else "None"
        return f"Crew(id={self.id}, name='{self.paddler.name}', club_id={club_id}, entry_id={entry_id})"

    def __str__(self):
        club = f" ({self.club.code})" if self.club else ""
        return f"{self.paddler.name}{club}"

    @property
    def team(self):
        for team in self.paddler.teams:
            if self.entry.race.series_id == team.series_id:
                return team
        else:
            return None
