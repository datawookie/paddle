from .base import *
from .club import *


class Class(Base):
    __tablename__ = "class"

    id = Column(Integer, primary_key=True)
    label = Column(String)


class Boat(Base):
    __tablename__ = "boat"

    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey(Class.id), index=True)
    club_id = Column(Integer, ForeignKey(Club.id), index=True)
    number = Column(Integer)
