import re

from .base import *


class Series(Base):
    __tablename__ = "series"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Series(name='{self.name}')"

    @property
    def slug(self):
        return re.sub("[^a-zA-Z0-9]+", "-", self.name).lower()
