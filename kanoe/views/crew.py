from .common import *


@blueprint.route("/crew/<crew_id>", methods=("GET", "POST"))
def crew(crew_id):
    crew = session.query(db.Crew).get(crew_id)

    if request.method == "POST":
        paddler_id = request.form["paddler"]
        club_id = request.form["club"] or None
        team_id = request.form.get("team") or None
        services = request.form.get("services", None)
        paid = request.form["paid"] or None

        crew.paddler_id = paddler_id
        crew.club_id = club_id
        crew.team_id = team_id if team_id else None
        if services:
            crew.services = True
        else:
            crew.services = False
        crew.paid = paid
        session.commit()

        flash("Updated crew.", "success")

        return redirect(url_for("kanoe.entry", entry_id=crew.entry.id))

    paddlers = session.query(db.Paddler).order_by(db.Paddler.name).all()
    clubs = session.query(db.Club).all()
    teams = (
        session.query(db.Team)
        .filter(db.Team.series_id == crew.entry.race.series_id)
        .all()
    )
    return render_template(
        "crew.j2", crew=crew, paddlers=paddlers, clubs=clubs, teams=teams
    )
