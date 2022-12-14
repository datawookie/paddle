from .base import *


class Club(Base):
    __tablename__ = "club"

    id = Column(String(3), primary_key=True)
    name = Column(String)

    def __repr__(self):
        return "Club('%s', '%s')" % (self.id, self.name)

    def __str__(self):
        return f"{self.name} ({self.id})"
