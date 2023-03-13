from .base import *


class AgeGroup(Base):
    __tablename__ = "age_group"

    id = Column(Integer, primary_key=True)
    label = Column(String)

    def __str__(self):
        return self.label

    @property
    def abbreviation(self):
        return self.label[0]
