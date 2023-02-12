import re
import datetime
import logging


UPLOAD_FOLDER = "/tmp"


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


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
    time = parse_time(time)
    time_min = parse_time(time_min)
    time_max = parse_time(time_max)
    return (time >= time_min) & (time <= time_max)


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"xlsx"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
