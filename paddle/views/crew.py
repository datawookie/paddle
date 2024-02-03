from .common import *


@blueprint.route("/crew/<crew_id>", methods=("GET", "POST"))
@login_required
def crew(crew_id):
    crew = session.get(db.Crew, crew_id)

    if request.method == "POST":
        paddler_id = request.form["paddler"]
        club_id = request.form.get("club", None)
        team_id = request.form.get("team", None)
        services = request.form.get("services", "0") == "1"
        paid = request.form["paid"] or None

        if club_id is not None:
            if club_id == "":
                club_id = None
            else:
                club_id = int(club_id)
                club = session.get(db.Club, club_id)
                if crew.club_id == club_id:
                    logging.info("Not changing club.")
                else:
                    if crew.club_id is None:
                        logging.info("Setting club.")
                    else:
                        logging.info("Changing club.")

                    if not crew.services and club.services:
                        logging.info("Setting services because club is services.")
                        services = True

        crew.club_id = club_id

        crew.paddler_id = paddler_id
        crew.team_id = team_id if team_id else None
        crew.services = services
        crew.paid = paid
        session.commit()

        flash("Updated crew.", "success")

        return redirect(url_for("kanoe.entry", entry_id=crew.entry.id))

    paddlers = session.query(db.Paddler).order_by(db.Paddler.name).all()
    clubs = session.query(db.Club).order_by(db.Club.name).all()
    teams = (
        session.query(db.Team)
        .filter(db.Team.series_id == crew.entry.race.series_id)
        .all()
    )
    return render_template(
        "crew.j2", crew=crew, paddlers=paddlers, clubs=clubs, teams=teams
    )


@blueprint.route(
    "/crew/<crew_id>/delete",
    methods=(
        "GET",
        "POST",
    ),
)
@login_required
def crew_delete(crew_id):
    crew = session.get(db.Crew, crew_id)
    entry_id = crew.entry.id

    session.delete(crew)
    session.commit()

    return redirect(url_for("kanoe.entry", entry_id=entry_id))
