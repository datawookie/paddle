from .base import *


class Person(Base):
    __tablename__ = "person"

    id = Column(Integer, primary_key=True)
    bcu = Column(Integer)  # BCU = British Canoe Union
    division = Column(Integer)
    salutation = Column(String)
    first = Column(String)
    middle = Column(String)
    last = Column(String)
    suffix = Column(String)
    dob = Column(Date)
    address = Column(String)
    email = Column(String)
    phone = Column(String)

    @property
    def name(self):
        name = [self.first, self.middle, self.last]
        name = list(filter(lambda item: item is not None, name))
        name = " ".join(name)
        name = name.strip()
        return name

    def __repr__(self):
        return f"Person(name='{self.name}')"
