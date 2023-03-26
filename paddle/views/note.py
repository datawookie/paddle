import logging
from flask_login import login_required

from .common import *


@blueprint.route("/entry/note/add/<entry_id>", methods=("GET", "POST"))
@login_required
def entry_note_update(entry_id):
    entry = session.get(db.Entry, entry_id)

    if request.method == "POST":
        if "delete" in request.form:
            note = None
        else:
            note = request.form.get("note").strip()
            if note == "":
                note = None

        entry.note = note
        session.commit()

        return redirect(url_for("kanoe.entry", entry_id=entry.id))

    return render_template("entry-note.j2", entry=entry)
