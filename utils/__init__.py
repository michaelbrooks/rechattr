from datetime import datetime, timedelta
from dateutil.tz import tzoffset, tzutc

from csrf import csrf_protected, csrf_token_input

_utc = tzutc()

zeroTime = timedelta(seconds=0)
oneMinute = timedelta(minutes=1)
oneHour = timedelta(hours=1)
oneDay = timedelta(days=1)

time_formats = {
    'seconds': ("%ds", "%d seconds"),
    'minutes': ("%dm", "%d minutes"),
    'hours': ("%dh", "%d hours"),
    'days': ("%dd", "%d days"),
    'date': ("%d %b", "%d %b %Y"),
}
def format_time(unit, value, type):
    typeIndex = 1 if long else 0
    format = time_formats[unit][typeIndex]
    if unit == 'date':
        return value.strftime(format)
    else:
        result = format %(value)
        if long and value == 1:
            return result[:-1]
        else:
            return result

# Forces a datetime into utc
def utc_aware(dt=None):
    if dt is None:
        dt = datetime.utcnow()
    return dt.replace(tzinfo=_utc)

def time_to(dt, long=False, showDays=False):
    now = utc_aware()
    delta = dt - now
    
    if delta < zeroTime:
        return format_time('seconds', 0, long)
    elif delta < oneMinute:
        return format_time('seconds', delta.seconds, long)
    elif delta < oneHour:
        return format_time('minutes', round(delta.seconds / 60), long)
    elif delta < oneDay:
        return format_time('hours', round(delta.seconds / (60*60)), long)
    elif showDays:
        return format_time('days', delta.days, long)
    else:
        return format_time('date', dt, long)
    
def time_ago(dt, long=False, showDays=False):
    now = utc_aware()
    delta = now - dt
    
    if delta < zeroTime:
        return format_time('seconds', 0, long)
    elif delta < oneMinute:
        return format_time('seconds', delta.seconds, long)
    elif delta < oneHour:
        return format_time('minutes', round(delta.seconds / 60), long)
    elif delta < oneDay:
        return format_time('hours', round(delta.seconds / (60*60)), long)
    elif showDays:
        return format_time('days', delta.days, long)
    else:
        return format_time('date', dt, long)

def parse_tweep_error(e):
    try:
        error = e.args[0][0] # the first error from the first argument
        message = error['message']
        code = error['code']
        return code, message
    except:
        return -1, str(e)