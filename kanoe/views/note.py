import logging

from .common import *


@blueprint.route("/entry/note/add/<entry_id>", methods=("GET", "POST"))
def entry_note_add(entry_id):
    if request.method == "POST":
        note = request.form.get("note")
        entry = session.query(db.Entry).get(entry_id)
        entry.note = note
        session.commit()

        return redirect(url_for("kanoe.entry", entry_id=entry.id))

    return render_template("entry-note.j2")


@blueprint.route("/entry/note/delete/<entry_id>", methods=("GET", "POST"))
def entry_note_delete(entry_id):
    entry = session.query(db.Entry).get(entry_id)
    entry.note = None
    session.commit()

    return redirect(url_for("kanoe.entry", entry_id=entry.id))
