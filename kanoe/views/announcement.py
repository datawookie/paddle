import logging
from flask_login import login_required

from .common import *


@blueprint.route("/announcement")
@login_required
def announcement():
    announcements = session.query(db.Announcement).all()
    return render_template("announcement.j2", announcements=announcements)


@blueprint.route("/announcement/<announcement_id>", methods=("GET", "POST"))
@login_required
def announcement_update(announcement_id):
    announcement = session.query(db.Announcement).get(announcement_id)

    if request.method == "POST":
        if "delete" in request.form:
            session.delete(announcement)
        else:
            announcement.enabled = "enabled" in request.form
            announcement.text = request.form.get("text")

        session.commit()

        return redirect(url_for("kanoe.announcement"))

    return render_template("announcement-update.j2", announcement=announcement)


@blueprint.route("/announcement/create")
@login_required
def announcement_create():
    announcement = db.Announcement()
    session.add(announcement)
    session.commit()

    return redirect(
        url_for("kanoe.announcement_update", announcement_id=announcement.id)
    )
