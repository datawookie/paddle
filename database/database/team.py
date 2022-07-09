from .base import *

# A Junior Team comprises of between 3 and 8 paddlers, with at least 3 boats,
# from any class, provided that all paddlers are under 19.  
# A Senior Team comprises of between 3 and 8 paddlers, with at least 3 boats,
# from any class. A Senior Team may include one or more junior crews. The Team
# time is calculated by adding up the times of the fastest three boats at each
# race. The members of the Team must be nominated before the start of the
# Series, after which no changes to the membership of the Team will be allowed.
# Crew pairings, within the nominated team members, may change and K1s can race
# instead of K2s. In each race, 3 boats, paddled by nominated team members must
# finish to qualify for the team event.

class Team(Base):
    __tablename__ = "team"

    id = Column(Integer, primary_key=True)
    name = Column(String)
