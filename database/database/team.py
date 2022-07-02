from .base import *


class Team(Base):
    __tablename__ = "team"

    id = Column(Integer, primary_key=True)
    name = Column(String)
