import enum

from .base import *
from .series import Series

# A Junior Team comprises of between 3 and 8 paddlers, with at least 3 boats,
# from any class, provided that all paddlers are under 19. A Senior Team
# comprises of between 3 and 8 paddlers, with at least 3 boats, from any class.
# A Senior Team may include one or more junior crews. The Team time is
# calculated by adding up the times of the fastest three boats at each race. The
# members of the Team must be nominated before the start of the Series, after
# which no changes to the membership of the Team will be allowed. Crew pairings,
# within the nominated team members, may change and K1s can race instead of K2s.
# In each race, 3 boats, paddled by nominated team members must finish to
# qualify for the team event.

# Team Rules - Most are defined in the Waterside Rules, but in summary and with
# a bit more explanation:
#
# There are up to 8 Members in a team Teams have to be nominated by the end of
# the Start window of Race A [ But there has been a few exceptions - especially
# if Race A is effected, No Juniors/Cancelled etc..- so not hard and fast ] A
# team has to be of a common denominator, Same Club, Same School ( full/part
# time education at that School ) The Junior teams have to be all Juniors Senior
# Teams can have junior members ( inc. Junior Vets ) Team members can be male or
# female and in any respective class. Only boats with Team members count toward
# the team. [ if K1 - Team members count, if K2 then BOTH members have to be
# team members [ K2’s can have any team members in any combination to count Only
# the FASTEST three boats in any class ( Doubles or singles ) count towards the
# team for any one Race It is the three fastest times for each race that get
# added together to achieve SERIES time Team prizes are awarded for only the
# Series in which all four races are run. ( we have made exception in some years
# and awarded Series prizes when only 3 races have been run.. Team members can
# race outside of a team but their results will not contribute [ Ie. Paddle K1
# in Race A, C & D for the team but pair up with a non-Team member at Race B,
# The race B result will not Count. ] A team has to have at least 3 team results
# in each Race to qualify for a Series Team result
#
# I think this answers your questions… and maybe a bit more !! Can anyone else
# think of anything I have overlooked..?

# I think it is fair to say that although you could flag up team anomalies (
# different Clubs etc ) but don’t make this FIXED, leave rules that you can
# identify but are admin rules flag up, but allow overrides.
#
# Rules that are data based ( eg, 3 results from each Race to qualify ) if only
# two results Qualified for any individual Race, then they miss the Series
# criteria and would not get/qualify for a Series result.
#
# It is also best to not make the Junior/Senior criteria fixed for any Junior
# Class as we can not guarantee from the BC data that their Age status is
# correct - Flag as a warning but DO allow overrides.
#
# It would also be useful to flag any validations at the point of entry but also
# to permit a post entry validation check of all programmed rules on data such
# as age, so these can be processed at a point post data entry, [ Data may be
# entered by a volunteer types and not some particularly knowledgable of the
# rules ]  A status on say a home screen such as a yellow  / orange / Red flags
# with Number counts to indicate quantity of flags of varying data breaking the
# validation rules.  This would also necessitate a flag on the record that this
# data validation has been overused and is acceptable.  EG. Senior paddler in a
# junior category due to either wrong information or date of birthday anomaly -
# as identified a while ago.
#
# See rules, but a junior is someone ho is UNDER 19 on the 1st Jan of the Series
# year. So someone whose 19th birthday falls say in January WILL be classified
# as a SNR for BC purposes but still a junior for Watersides.  The Marathon
# Racing Handbook defines the age category as “ as defined by their BC
# membership “ - So this may mean that BC paddlers age category may well be 18
# or over on any one day for juniors, So BC may change a paddlers status to
# Senior on the paddlers 18th Birthday, but that is NOT the ruling for
# Watersides [ which is in alignment with the DW Race ].
#
# This varying discretion also applies for Masters and Veterans.

# Andrew,  Just re- reading the line:  Only the FASTEST three boats in any class
# ( Doubles or singles ) count towards the team for any one Race
#
# I think this may need a bit more clarification for the programming to work…
#
# Any qualifying result from ANY appropriate class (Junior/Senior) potentialy
# counts towards the Team result for that Race Only the fastest THREE results
# for that RACE count towards the Series time. It is the aggregate of all the
# Team’s top 3 results from all Races that provides the Series Total and it is
# this that is used to place the teams in Series Order.
#
# Note: Not necessary for the first version, but it would be useful to have a
# display ( printable ) of all team members results and if they qualify and or
# Count towards the Team’s Series total Race by Race and for the Series.
#
# Note: we usually also print a Series Result thus far at the End of Race C.
#
# Also Note Results for Races are published on the day during the Race as a
# scrolling display, but are printed to a PDF first as a Provisional and then
# after reconciliation of any challenges usually but the Wednesday/Thursday
# following the Race as a Final result, it is then that the Series Result thus
# far is published after Race C.
#
# Also to clarify, you may need to flexible about qualifying races for Series
# Results - If say Race B was cancelled due to bad weather say, we may still
# want to award a Series result.  [ We do this currently by copying any of the
# other race results [ usually A ] and change the results files so they show a
# result of 1 second. The existing system software then validates for a Series
# it also copes with duplicate times ie, 1 second for all team members would
# just mean that the team adds just 3 seconds to the Series not any more…!


class TeamType(Base):
    __tablename__ = "team_type"

    id = Column(Integer, primary_key=True)
    label = Column(String)


class Team(Base):
    __tablename__ = "team"
    __table_args__ = (
        UniqueConstraint("name", "series_id", name="uq_team_name_series"),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String)
    team_type_id = Column(Integer, ForeignKey(TeamType.id), nullable=False)
    series_id = Column(Integer, ForeignKey(Series.id), index=True, nullable=False)

    type = relationship(TeamType, backref="teams")
    series = relationship(Series, backref="teams", lazy="joined")

    def __str__(self):
        return self.name
