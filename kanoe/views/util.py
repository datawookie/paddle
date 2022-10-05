import re
import datetime
import logging


def time_strip_colons(time):
    time = re.sub(":", "", time)
    logging.debug(f"- Removed colons: {time}")
    return time


def parse_time(time):
    if not time:
        return None
    logging.debug(f"Parsing time: {time}")
    time = time_strip_colons(time)
    if len(time) != 6:
        raise RuntimeError("Time too short (should have form HHMMSS or HH:MM:SS).")
    time = datetime.datetime.strptime(time, "%H%M%S")
    time = time.strftime("%H:%M:%S")
    logging.debug(f"- Normalised: {time}")
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
