from .base import *


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

    # This is the version which is used in Python.
    #
    @hybrid_property
    def name(self):
        name = [self.first, self.middle, self.last]
        name = list(filter(lambda item: item is not None, name))
        name = " ".join(name)
        name = name.strip()
        return name

    # This is the version which is used in SQLAlchemy expressions (like sorting).
    #
    @name.expression
    def name(cls):
        return cls.first + " " + cls.last

    def __repr__(self):
        return f"Paddler(name='{self.name}')"

    def __str__(self):
        return self.name
