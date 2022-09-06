from .base import *


class Paddler(Base):
    __tablename__ = "paddler"

    id = Column(Integer, primary_key=True)
    bcu = Column(Integer)  # BCU = British Canoe Union
    bcu_expiry = Column(Date)
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
        return f"Paddler(name='{self.name}')"
