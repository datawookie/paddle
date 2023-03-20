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
    team = session.get(db.Team, team_id)

    entries = set()
    #
    for crew in team.crews:
        entries.add(crew.entry)

    # Keep only team entries.
    #
    # This will eliminate, for example, K2 crews where one of the paddlers is not on
    # the team.
    #
    entries = [entry for entry in entries if entry.team == team]

    races = list(set([entry.race for entry in entries]))
    races = sorted(races, key=lambda race: race.date)
    races = {race: {"entries": []} for race in races}

    for entry in entries:
        if entry.time:
            races[entry.race]["entries"].append(entry)

    for race in races:
        races[race]["entries"] = sorted(
            races[race]["entries"], key=lambda entry: entry.time
        )
        top = races[race]["entries"][:3]
        if len(top) == 3:
            races[race]["time"] = sum(
                [entry.time for entry in top], datetime.timedelta()
            )
        else:
            races[race]["time"] = None

    return render_template(
        "team.j2",
        team=team,
        races=races,
    )
