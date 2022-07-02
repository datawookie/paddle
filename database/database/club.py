from .base import *


class Club(Base):
    __tablename__ = "club"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String)
