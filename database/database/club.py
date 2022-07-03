from .base import *


class Club(Base):
    __tablename__ = "club"

    id = Column(Integer, primary_key=True)
    code = Column(String)
    name = Column(String)

    def __repr__(self):
        return "Club('%s', '%s')" % (self.code, self.name)
