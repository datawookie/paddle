# Standard Library
import enum
from datetime import date

from .age_group import AgeGroup
from .base import *


def combine_names(first, middle, last):
    name = [first, middle, last]
    name = list(filter(lambda item: item is not None, name))
    name = " ".join(name)
    name = name.strip()
    return name


class MembershipBody(Base):
    __tablename__ = "membership_body"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    acronym = Column(String)


class Paddler(Base):
    __tablename__ = "paddler"

    id = Column(Integer, primary_key=True)
    membership_number = Column(Integer)
    membership_expiry = Column(Date)
    membership_body_id = Column(Integer, ForeignKey(MembershipBody.id))
    division = Column(Integer)
    title = Column(String)
    first = Column(String)
    middle = Column(String)
    last = Column(String)
    gender = Column(String(1))
    suffix = Column(String)
    dob = Column(Date)
    address = Column(String)
    email = Column(String)
    phone = Column(String)
    emergency_name = Column(String)
    emergency_phone = Column(String)
    age_group_id = Column(Integer, ForeignKey(AgeGroup.id), index=True)

    age_group = relationship(AgeGroup, backref="paddlers", lazy="joined")
    membership_body = relationship(MembershipBody, backref="paddlers", lazy="joined")

    teams = relationship("Team", secondary="team_paddler", back_populates="paddlers")

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

    @property
    def membership(self):
        membership = self.membership_number
        if membership and self.membership_body:
            membership = self.membership_body.acronym + str(membership)
        return membership

    @property
    def membership_expired(self):
        if self.membership_expiry:
            return self.membership_expiry < date.today()
        else:
            return True

    @property
    def age(self):
        # This is the age at the beginning of the year.
        newyear = date(date.today().year, 1, 1)

        age = newyear.year - self.dob.year

        # Adjust if birthday has not occurred yet this year.
        #
        if (self.dob.month, self.dob.day) > (newyear.month, newyear.day):
            age -= 1

        return age

    @property
    def age_group_calculated(self):
        age = self.age
        if not age:
            return None
        elif age < 19:
            return "Junior"
        elif age >= 50:
            return "Master"
        elif age >= 35:
            return "Veteran"
        else:
            return "Senior"
