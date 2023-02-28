from .base import *


class Club(Base):
    __tablename__ = "club"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    code_regex = Column(String())

    def __repr__(self):
        return "Club(%d, '%s')" % (self.id, self.name)

    def __str__(self):
        return f"{self.name}"

    @property
    def code(self):
        return self.code_regex.split("|")[0]
