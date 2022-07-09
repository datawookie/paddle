from .base import *


class Type(Base):
    __tablename__ = "type"

    id = Column(Integer, primary_key=True)
    label = Column(String)
