import datetime
import isodate
import json
import settings
import uuid

def extract_values(data):
    # Extract some things to pass as attributes for Backtrace.
    data = json.loads(data)
    if data.get('TelemetryEnvironment', None):
        env = json.loads(data['TelemetryEnvironment'])
        # Get useful bits out of TelemetryEnvironment
        data['os_name'] = env['system']['os']['name']
        data['os_version'] = env['system']['os']['version']
        data['cpu_arch'] = env['build']['architecture']

    # Delete unwanted attributes.
    for key in settings.skip_attributes:
        data.pop(key, None)
    return data

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
    return "bp-%s%d%02d%02d%02d" % (
        id_[:-7],
        throttle_result,
        timestamp.year % 100,
        timestamp.month,
        timestamp.day,
    )
