from ...common import *
from ...entry import load_entries, load_xlsx


@blueprint.route("/race/<race_id>/entries/import/xlsx", methods=("GET", "POST"))
@login_required
def race_entry_bulk(race_id):
    race = session.get(db.Race, race_id)

    if request.method == "POST":
        file = request.files.get("file")
        if file and allowed_file(file.filename):
            logging.debug(f"Entries file: {file.filename}")
            filename = secure_filename(file.filename)
            logging.debug(f"Entries file: {filename} (secure)")
            filename = os.path.join(UPLOAD_FOLDER, filename)
            logging.debug(f"Entries file: {filename} (upload path)")
            file.save(filename)

            logging.debug("Reading entries from XLSX file.")
            entries = load_xlsx(filename)
            logging.debug("Adding entries.")
            load_entries(race, entries)

        return redirect(url_for("paddle.races"))

    return render_template(
        "race-entries-bulk.j2",
        race=race,
    )
