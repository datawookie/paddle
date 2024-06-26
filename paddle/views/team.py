import functools
import logging
import operator

from .common import *
from .series import series_team
from .util import hhmmss


@blueprint.route("/teams")
@login_required
def teams():
    teams = (
        session.query(db.Team).order_by(db.Team.series_id.desc(), db.Team.name).all()
    )
    return render_template("teams.j2", teams=teams)


@blueprint.route("/team/create", methods=("GET", "POST"))
@login_required
def team_create():
    if request.method == "POST":
        name = request.form["name"]
        team_type_id = request.form["team_type"]
        series_id = request.form["series"]

        team = db.Team(name=name, series_id=series_id, team_type_id=team_type_id)
        session.add(team)
        session.commit()

        return redirect(url_for("paddle.teams"))

    types = session.query(db.TeamType).all()
    serieses = session.query(db.Series).order_by(db.Series.name.desc()).all()
    return render_template(
        "team-create.j2",
        serieses=serieses,
        types=types,
    )


@blueprint.route("/team/<team_id>")
@login_required
def team(team_id):
    team, races = series_team(team_id)

    total = [data["time"] for _, data in races.items()]
    try:
        if len(total) == 4:
            total = functools.reduce(operator.add, total)
            total = hhmmss(total)
        else:
            total = None
    except TypeError:
        total = None

    return render_template(
        "series-results-team.j2",
        team=team,
        races=races,
        total=total,
    )
