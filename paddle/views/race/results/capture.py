import logging

from ...common import *


@blueprint.route("/race/<race_id>/results/capture", methods=("GET", "POST"))
@login_required
def race_results_capture(race_id):
    if request.method == "POST":
        entry_id = request.form["entry_id"]
        time_start = request.form.get("time_start")
        time_finish = request.form.get("time_finish")
        time_adjustment = request.form.get("time_adjustment")
        note = request.form.get("note")
        scratched = request.form.get("scratched", False)
        retired = request.form.get("retired", False)
        disqualified = request.form.get("disqualified", False)

        time_start = parse_time(time_start)
        time_finish = parse_time(time_finish)

        entry = session.get(db.Entry, entry_id)

        # Start time.
        if time_start:
            entry.time_start = time_start
        if not time_start and entry.time_start:
            logging.info("Remove start time.")
            entry.time_start = None
        # Finish time.
        if time_finish:
            entry.time_finish = time_finish
        if not time_finish and entry.time_finish:
            logging.info("Remove finish time.")
            entry.time_finish = None

        if time_adjustment:
            entry.time_adjustment = time_adjustment
        if scratched:
            entry.scratched = True
        else:
            entry.scratched = False
        if retired:
            entry.retired = True
        else:
            entry.retired = False
        if disqualified:
            entry.disqualified = True
        else:
            entry.disqualified = False
        if note:
            entry.note = note

        session.commit()

        message = []
        #
        if entry.scratched:
            message = ["scratched"]
        elif entry.disqualified:
            message = ["disqualified"]
        elif entry.retired:
            message = ["retired"]
        else:
            if entry.time_start:
                message.append(f"start: {entry.time_start}")
            if entry.time_finish:
                message.append(f"finish: {entry.time_finish}")
        #
        if message:
            message = "; ".join(message)
        else:
            message = ""
        #
        message = str(entry) + " — " + message + "."

        flash(message, "success")

        return redirect(url_for("kanoe.race_results_capture", race_id=race_id))

    race = session.get(db.Race, race_id)

    return render_template("race-results-capture.j2", race=race)
