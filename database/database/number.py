from .base import *

MAX_NUMBER = 599


class Number(Base):
    __tablename__ = "number"

    id = Column(Integer, primary_key=True)
    lost = Column(Boolean)

    def __repr__(self):
        return "Number(%d, lost=%s)" % (self.id, self.lost)

    def __str__(self):
        return str(self.id)
