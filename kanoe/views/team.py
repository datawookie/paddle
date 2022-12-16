from .common import *


@blueprint.route("/teams")
def teams():
    teams = session.query(db.Team).all()
    return render_template("teams.j2", teams=teams)


@blueprint.route("/team/create", methods=("GET", "POST"))
def team_create():
    if request.method == "POST":
        name = request.form["name"]
        series_id = request.form["series"]

        team = db.Team(name=name, series_id=series_id)
        session.add(team)
        session.commit()

        return redirect(url_for("kanoe.teams"))

    serieses = session.query(db.Series).order_by(db.Series.name.desc()).all()
    return render_template("team-create.j2", serieses=serieses)
