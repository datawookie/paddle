import logging
from flask_login import login_required

from .common import *

# ADD LOGIN_REQUIRED

# ADD LOGIN_REQUIRED

# ADD LOGIN_REQUIRED

# ADD LOGIN_REQUIRED

# ADD LOGIN_REQUIRED

# ADD LOGIN_REQUIRED

# ADD LOGIN_REQUIRED


@blueprint.route("/announcement")
def announcement():
    announcements = session.query(db.Announcement).all()
    return render_template("announcement.j2", announcements=announcements)


@blueprint.route("/announcement/<announcement_id>", methods=("GET", "POST"))
def announcement_update(announcement_id):
    announcement = session.query(db.Announcement).get(announcement_id)

    if request.method == "POST":
        logging.info(request.form)
        if "delete" in request.form:
            session.delete(announcement)
        else:
            announcement.enabled = "enabled" in request.form
            announcement.text = request.form.get("text")

        session.commit()

        return redirect(url_for("kanoe.announcement"))

    return render_template("announcement-update.j2", announcement=announcement)


@blueprint.route("/announcement/create")
def announcement_create():
    announcement = db.Announcement()
    session.add(announcement)
    session.commit()

    return redirect(
        url_for("kanoe.announcement_update", announcement_id=announcement.id)
    )
