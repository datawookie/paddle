import re
import datetime
import logging


UPLOAD_FOLDER = "/tmp"


def time_strip_colons(time):
    time = re.sub(":", "", time)
    logging.debug(f"- Removed colons: {time}")
    return time


def parse_time(time):
    if not time:
        return None
    logging.debug(f"Parsing time:     {time}")
    time = time_strip_colons(time)
    if len(time) == 2:
        time += "0000"
    elif len(time) == 4:
        time += "00"
    elif len(time) != 6:
        raise RuntimeError(
            f"Invalid time '{time}' (should have form HHMMSS or HH:MM:SS)."
        )
    time = datetime.datetime.strptime(time, "%H%M%S")
    time = time.strftime("%H:%M:%S")
    logging.debug(f"- Normalised:     {time}")
    return time


def time_pad_seconds(time):
    time = time_strip_colons(time)
    if len(time) == 4:
        time = time + "00"
    return time


def time_between(time, time_min, time_max):
    logging.debug(f"Check if {time} is between {time_min} and {time_max}.")
    time = parse_time(time)
    time_min = parse_time(time_min)
    time_max = parse_time(time_max)
    return (time >= time_min) & (time <= time_max)


# Convert timedelta into HHMMSS format. This is important when duration longer than 1 day.
#
def hhmmss(delta):
    ss = delta.total_seconds()

    hh = ss // 3600
    ss = ss % 3600
    mm = ss // 60
    ss = ss % 60

    return "%d:%02d:%02d" % (hh, mm, ss)


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"xlsx"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def empty_to_none(text):
    if text == "":
        return None
    else:
        return text


def argument_boolean(arg):
    return arg in ["True", "true", "1"]
