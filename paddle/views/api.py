from .common import *


@blueprint.route("/api/get-entry", methods=("GET", "POST"))
def get_entry():
    if request.method == "POST":
        race_id = request.form["race_id"]
        # Get race number.
        race_number = request.form["race_number"]
        try:
            race_number = (
                session.query(db.Number)
                .filter(
                    db.Number.id == race_number,
                )
                .one()
            )
        except db.NoResultFound:
            logging.warning(f"🚨 Race number {race_number} not found.")
            abort(404)
        # Get corresponding entry.
        try:
            entry = (
                session.query(db.Entry)
                .filter(
                    db.Entry.race_id == race_id,
                    db.Entry.race_number == race_number,
                )
                .one()
            )
        except db.NoResultFound:
            logging.warning(f"🚨 Entry for race number {race_number} not found.")
            abort(404)
        data = {
            "entry_id": entry.id,
            "paddlers": str(entry),
            "time_start": entry.time_start,
            "time_finish": entry.time_finish,
            "time_adjustment": entry.time_adjustment,
            "scratched": entry.scratched,
            "retired": entry.retired,
            "disqualified": entry.disqualified,
            "note": entry.note,
        }
        return jsonify(data)


@blueprint.route("/api/update", methods=("GET", "POST"))
def update():
    if request.method == "POST":
        try:
            field = request.form["field"]
            value = request.form["value"]
            edit_id = request.form["edit_id"]

            entry = session.get(db.Entry, edit_id)

            if field == "start":
                entry.time_start = value
            if field == "finish":
                entry.time_finish = value

            session.commit()

            success = 1
        except:
            success = 0

        return jsonify(success)
