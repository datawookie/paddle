from .common import *


@blueprint.route("/clubs")
def clubs():
    clubs = session.query(db.Club).all()
    return render_template("clubs.j2", clubs=clubs)


@blueprint.route("/club/<club_id>")
def club(club_id):
    club = session.query(db.Club).get(club_id)
    return render_template("club.j2", club=club)
