from .base import *
from .club import *
import enum


class BoatType(enum.Enum):
    K1 = 1
    K2 = 2
    C = 3


boat_type = Enum(BoatType)


class Boat(Base):
    __tablename__ = "boat"

    id = Column(Integer, primary_key=True)
    type = Column(boat_type, index=True)
    number = Column(Integer)
