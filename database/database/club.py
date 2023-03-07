from .base import *


class Club(Base):
    __tablename__ = "club"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    code_regex = Column(String())
    services = Column(Boolean, server_default=expression.false())

    def __repr__(self):
        return "Club(id=%d, name='%s', regex='%s')" % (
            self.id,
            self.name,
            self.code_regex,
        )

    def __str__(self):
        return f"{self.name}"

    @property
    def code(self):
        return self.code_regex.split("|")[0]
