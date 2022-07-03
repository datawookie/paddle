from .base import *


class Person(Base):
    __tablename__ = "person"

    id = Column(Integer, primary_key=True)
    bcu = Column(Integer)  # BCU = British Canoe Union
    salutation = Column(String)
    first = Column(String)
    middle = Column(String)
    last = Column(String)
    suffix = Column(String)
    dob = Column(Date)
    address = Column(String)
    phone = Column(String)
