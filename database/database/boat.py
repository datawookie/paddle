from .base import *
from .club import *
from .type import *


class Boat(Base):
    __tablename__ = "boat"

    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey(Type.id), index=True)
    number = Column(Integer)
