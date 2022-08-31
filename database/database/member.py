from .base import *


class Member(Base):
    __tablename__ = "member"

    id = Column(Integer, primary_key=True)
    first = Column(String)
    middle = Column(String)
    last = Column(String)
