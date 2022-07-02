from .base import *


class Series(Base):
    __tablename__ = "series"

    id = Column(Integer, primary_key=True)
