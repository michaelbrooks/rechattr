from datetime import datetime
from dateutil.tz import tzoffset, tzutc

_utc = tzutc()

# Forces a datetime into utc
def utc_aware(dt=None):
    if dt is None:
        dt = datetime.utcnow()
    return dt.replace(tzinfo=_utc)
