from dateutil.tz import tzoffset, tzutc
from datetime import datetime, timedelta
from dateutil.tz import tzoffset, tzutc

utc = tzutc()

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
    return dt.replace(tzinfo=utc)

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
        
def user_to_datetime(date_str, time_str, gmt_offset_seconds):
    date_time_str = "%s %s" %(date_str, time_str)
    parsed = datetime.strptime(date_time_str, "%m/%d/%Y %I:%M%p")
        
    tzinfo = tzoffset(None, gmt_offset_seconds);
    parsed = parsed.replace(tzinfo=tzinfo)
    
    return parsed.astimezone(utc)

def datetime_to_user(dt, gmt_offset_seconds):
    tzinfo = tzoffset(None, gmt_offset_seconds);
    dt = dt.astimezone(tzinfo)
    
    date_str = dt.strftime("%m/%d/%Y").lstrip('0')
    time_str = dt.strftime("%I:%M%p").lstrip('0').lower()
    
    return date_str, time_str
