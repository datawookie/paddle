from datetime import date
from .base import *
from .age_group import AgeGroup


def combine_names(first, middle, last):
    name = [first, middle, last]
    name = list(filter(lambda item: item is not None, name))
    name = " ".join(name)
    name = name.strip()
    return name


class Paddler(Base):
    __tablename__ = "paddler"

    id = Column(Integer, primary_key=True)
    bcu = Column(Integer)  # BCU = British Canoe Union
    bcu_expiry = Column(Date)
    division = Column(Integer)
    title = Column(String)
    first = Column(String)
    middle = Column(String)
    last = Column(String)
    suffix = Column(String)
    dob = Column(Date)
    address = Column(String)
    email = Column(String)
    phone = Column(String)
    emergency_name = Column(String)
    emergency_phone = Column(String)
    age_group_id = Column(Integer, ForeignKey(AgeGroup.id), index=True)

    age_group = relationship(AgeGroup, backref="paddlers", lazy="joined")

    # This is the version which is used in Python.
    #
    @hybrid_property
    def name(self):
        return combine_names(self.first, self.middle, self.last)

    # This is the version which is used in SQLAlchemy expressions (like sorting).
    #
    @name.expression
    def name(cls):
        return cls.first + " " + cls.last

    def __repr__(self):
        return f"Paddler(id={self.id}, name='{self.name}', division={self.division or '?'})"

    def __str__(self):
        return self.name

    @property
    def registered(self):
        if not self.bcu:
            # No BCU number.
            return False
        elif self.bcu_expiry and self.bcu_expiry <= date.today():
            # BCU number has expired.
            return False
        else:
            return True
