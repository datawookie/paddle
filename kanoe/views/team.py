from .common import *


@blueprint.route("/teams", methods=("GET", "POST"))
def teams():
    if request.method == "POST":
        name = request.form["name"]

        team = db.Team(name=name)
        session.add(team)
        session.commit()

        return redirect(url_for("kanoe.teams"))

    teams = session.query(db.Team).all()
    return render_template("teams.j2", teams=teams)
