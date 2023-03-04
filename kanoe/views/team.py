import logging
from flask_login import login_required

from .common import *


@blueprint.route("/teams")
@login_required
def teams():
    teams = session.query(db.Team).all()
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

        return redirect(url_for("kanoe.teams"))

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
    team = session.query(db.Team).get(team_id)

    entries = set()
    #
    for crew in team.crews:
        entries.add(crew.entry)

    return render_template(
        "team.j2",
        team=team,
        entries=entries,
    )
