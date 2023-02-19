import re
from .base import *


CATEGORY_LIST = [
    "K2 Senior",
    "K2 Junior",
    "K2 Ladies",
    "K2 Junior Ladies",
    "K2 Veteran",
    "K2 Mixed",
    "K2 Junior/Veteran",
    "K1 Senior",
    "K1 Junior",
    "K1 Ladies",
    "K1 Veteran",
    "C2",
    "C1",
]
GENDER_LIST = [
    "male",
    "female",
    "mixed",
]


class Category(Base):
    __tablename__ = "category"
    __table_args__ = (UniqueConstraint("label", name="uq_category_label"),)

    id = Column(Integer, primary_key=True)
    label = Column(String)

    def __repr__(self):
        return "Category('%s')" % (self.label)

    def __str__(self):
        return self.label

    def __eq__(self, other):
        return self.label == other

    @property
    def crew_count(self):
        return int(re.sub("[^12]+", "", self.label))
