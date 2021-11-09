import datetime
import isodate
import uuid

def utc_now():
    return datetime.datetime.now(isodate.UTC)

def create_crash_id(timestamp=None, throttle_result=1):
    """Generate a crash id.
    From: https://github.com/mozilla-services/antenna/blob/main/antenna/util.py#L97
    Crash ids have the following format::
        de1bb258-cbbf-4589-a673-34f800160918
                                     ^^^^^^^
                                     ||____|
                                     |  yymmdd
                                     |
                                     throttle_result
    The ``throttle_result`` should be either 0 (accept) or 1 (defer).
    :arg date/datetime timestamp: a datetime or date to use in the crash id
    :arg int throttle_result: the throttle result to encode; defaults to 1
        which is DEFER
    :returns: crash id as str
    """
    if timestamp is None:
        timestamp = utc_now().date()

    id_ = str(uuid.uuid4())
    return "%s%d%02d%02d%02d" % (
        id_[:-7],
        throttle_result,
        timestamp.year % 100,
        timestamp.month,
        timestamp.day,
    )
