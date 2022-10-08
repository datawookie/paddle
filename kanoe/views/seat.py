from .common import *


@blueprint.route("/seat/<seat_id>", methods=("GET", "POST"))
def seat(seat_id):
    seat = session.query(db.Seat).get(seat_id)

    if request.method == "POST":
        paddler_id = request.form["paddler"]
        club_id = request.form["club"]
        team_id = request.form.get("team")
        services = request.form.get("services", None)

        seat.paddler_id = paddler_id
        seat.club_id = club_id
        seat.team_id = team_id if team_id else None
        if services:
            seat.services = True
        else:
            seat.services = False
        session.commit()

        flash("Updated seat.", "success")

        return redirect(url_for("kanoe.entry", entry_id=seat.entry.id))

    paddlers = session.query(db.Paddler).order_by(db.Paddler.name).all()
    clubs = session.query(db.Club).all()
    teams = (
        session.query(db.Team)
        .filter(db.Team.series_id == seat.entry.race.series_id)
        .all()
    )
    return render_template(
        "seat.j2", seat=seat, paddlers=paddlers, clubs=clubs, teams=teams
    )
