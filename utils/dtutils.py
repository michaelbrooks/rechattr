from dateutil.tz import tzoffset, tzutc
from datetime import datetime, timedelta
from dateutil.tz import tzoffset, tzutc
import math
import pytz
import re
import calendar

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
    'date': ("%b", "%b %Y"),
}
def format_time(unit, value, long):
    typeIndex = 1 if long else 0
    format = time_formats[unit][typeIndex]
    if unit == 'date':
        tail = value.strftime(format)
        day = value.strftime('%d').lstrip('0')
        return "%s %s" %(day, tail)
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

def dt_timestamp(dt):
    return calendar.timegm(dt.utctimetuple())
    
def time_to(dt, dateFallback=False, long=False, showDays=False):
    now = utc_aware()
    delta = dt - now
    if dateFallback:
        return nice_delta(delta, dateFallback=dt, long=long, showDays=showDays)
    else:
        return nice_delta(delta, long=long, showDays=showDays)
    
def nice_delta(delta, dateFallback=None, long=False, showDays=False, sub=False):
    if delta < zeroTime:
        return format_time('seconds', 0, long)
    elif delta < oneMinute:
        return format_time('seconds', delta.seconds, long)
    elif delta < oneHour:
        return format_time('minutes', round(delta.seconds / 60.0), long)
    elif delta < oneDay:
        return format_time('hours', round(delta.seconds / (60.0*60)), long)
    elif showDays:
        return format_time('days', delta.total_seconds() / (60.0*60*24), long)
    else:
        return format_time('date', dateFallback, long)
        
def time_ago(dt, dateFallback=False, long=False, showDays=False):
    now = utc_aware()
    delta = now - dt
    if dateFallback:
        return nice_delta(delta, dateFallback=dt, long=long, showDays=showDays)
    else:
        return nice_delta(delta, long=long, showDays=showDays)
        
def user_to_datetime(date_str, time_str, olsonCode):
    zone = tz(olsonCode)
    
    date_time_str = "%s %s" %(date_str, time_str)
    parsed = datetime.strptime(date_time_str, "%m/%d/%Y %I:%M%p")
        
    return zone.localize(parsed)

def datetime_to_user(localDateTime):
    date_str = localDateTime.strftime("%m/%d/%Y").lstrip('0')
    time_str = localDateTime.strftime("%I:%M%p").lstrip('0').lower()
    
    return date_str, time_str

# These time zones are very very close to what Twitter provides.
# They come from ruby on rails:
# http://api.rubyonrails.org/classes/ActiveSupport/TimeZone.html
ruby_to_olson = {
    "International Date Line West":"Pacific/Midway",
    "Midway Island":"Pacific/Midway",
    "American Samoa":"Pacific/Pago_Pago",
    "Hawaii":"Pacific/Honolulu",
    "Alaska":"America/Juneau",
    "Pacific Time (US & Canada)":"America/Los_Angeles",
    "Tijuana":"America/Tijuana",
    "Mountain Time (US & Canada)":"America/Denver",
    "Arizona":"America/Phoenix",
    "Chihuahua":"America/Chihuahua",
    "Mazatlan":"America/Mazatlan",
    "Central Time (US & Canada)":"America/Chicago",
    "Saskatchewan":"America/Regina",
    "Guadalajara":"America/Mexico_City",
    "Mexico City":"America/Mexico_City",
    "Monterrey":"America/Monterrey",
    "Central America":"America/Guatemala",
    "Eastern Time (US & Canada)":"America/New_York",
    "Indiana (East)":"America/Indiana/Indianapolis",
    "Bogota":"America/Bogota",
    "Lima":"America/Lima",
    "Quito":"America/Lima",
    "Atlantic Time (Canada)":"America/Halifax",
    "Caracas":"America/Caracas",
    "La Paz":"America/La_Paz",
    "Santiago":"America/Santiago",
    "Newfoundland":"America/St_Johns",
    "Brasilia":"America/Sao_Paulo",
    "Buenos Aires":"America/Argentina/Buenos_Aires",
    "Georgetown":"America/Guyana",
    "Greenland":"America/Godthab",
    "Mid-Atlantic":"Atlantic/South_Georgia",
    "Azores":"Atlantic/Azores",
    "Cape Verde Is.":"Atlantic/Cape_Verde",
    "Dublin":"Europe/Dublin",
    "Edinburgh":"Europe/London",
    "Lisbon":"Europe/Lisbon",
    "London":"Europe/London",
    "Casablanca":"Africa/Casablanca",
    "Monrovia":"Africa/Monrovia",
    "UTC":"Etc/UTC",
    "Belgrade":"Europe/Belgrade",
    "Bratislava":"Europe/Bratislava",
    "Budapest":"Europe/Budapest",
    "Ljubljana":"Europe/Ljubljana",
    "Prague":"Europe/Prague",
    "Sarajevo":"Europe/Sarajevo",
    "Skopje":"Europe/Skopje",
    "Warsaw":"Europe/Warsaw",
    "Zagreb":"Europe/Zagreb",
    "Brussels":"Europe/Brussels",
    "Copenhagen":"Europe/Copenhagen",
    "Madrid":"Europe/Madrid",
    "Paris":"Europe/Paris",
    "Amsterdam":"Europe/Amsterdam",
    "Berlin":"Europe/Berlin",
    "Bern":"Europe/Berlin",
    "Rome":"Europe/Rome",
    "Stockholm":"Europe/Stockholm",
    "Vienna":"Europe/Vienna",
    "West Central Africa":"Africa/Algiers",
    "Bucharest":"Europe/Bucharest",
    "Cairo":"Africa/Cairo",
    "Helsinki":"Europe/Helsinki",
    "Kyiv":"Europe/Kiev",
    "Riga":"Europe/Riga",
    "Sofia":"Europe/Sofia",
    "Tallinn":"Europe/Tallinn",
    "Vilnius":"Europe/Vilnius",
    "Athens":"Europe/Athens",
    "Istanbul":"Europe/Istanbul",
    "Minsk":"Europe/Minsk",
    "Jerusalem":"Asia/Jerusalem",
    "Harare":"Africa/Harare",
    "Pretoria":"Africa/Johannesburg",
    "Moscow":"Europe/Moscow",
    "St. Petersburg":"Europe/Moscow",
    "Volgograd":"Europe/Moscow",
    "Kuwait":"Asia/Kuwait",
    "Riyadh":"Asia/Riyadh",
    "Nairobi":"Africa/Nairobi",
    "Baghdad":"Asia/Baghdad",
    "Tehran":"Asia/Tehran",
    "Abu Dhabi":"Asia/Muscat",
    "Muscat":"Asia/Muscat",
    "Baku":"Asia/Baku",
    "Tbilisi":"Asia/Tbilisi",
    "Yerevan":"Asia/Yerevan",
    "Kabul":"Asia/Kabul",
    "Ekaterinburg":"Asia/Yekaterinburg",
    "Islamabad":"Asia/Karachi",
    "Karachi":"Asia/Karachi",
    "Tashkent":"Asia/Tashkent",
    "Chennai":"Asia/Kolkata",
    "Kolkata":"Asia/Kolkata",
    "Mumbai":"Asia/Kolkata",
    "New Delhi":"Asia/Kolkata",
    "Kathmandu":"Asia/Kathmandu",
    "Astana":"Asia/Dhaka",
    "Dhaka":"Asia/Dhaka",
    "Sri Jayawardenepura":"Asia/Colombo",
    "Almaty":"Asia/Almaty",
    "Novosibirsk":"Asia/Novosibirsk",
    "Rangoon":"Asia/Rangoon",
    "Bangkok":"Asia/Bangkok",
    "Hanoi":"Asia/Bangkok",
    "Jakarta":"Asia/Jakarta",
    "Krasnoyarsk":"Asia/Krasnoyarsk",
    "Beijing":"Asia/Shanghai",
    "Chongqing":"Asia/Chongqing",
    "Hong Kong":"Asia/Hong_Kong",
    "Urumqi":"Asia/Urumqi",
    "Kuala Lumpur":"Asia/Kuala_Lumpur",
    "Singapore":"Asia/Singapore",
    "Taipei":"Asia/Taipei",
    "Perth":"Australia/Perth",
    "Irkutsk":"Asia/Irkutsk",
    "Ulaan Bataar":"Asia/Ulaanbaatar",
    "Seoul":"Asia/Seoul",
    "Osaka":"Asia/Tokyo",
    "Sapporo":"Asia/Tokyo",
    "Tokyo":"Asia/Tokyo",
    "Yakutsk":"Asia/Yakutsk",
    "Darwin":"Australia/Darwin",
    "Adelaide":"Australia/Adelaide",
    "Canberra":"Australia/Melbourne",
    "Melbourne":"Australia/Melbourne",
    "Sydney":"Australia/Sydney",
    "Brisbane":"Australia/Brisbane",
    "Hobart":"Australia/Hobart",
    "Vladivostok":"Asia/Vladivostok",
    "Guam":"Pacific/Guam",
    "Port Moresby":"Pacific/Port_Moresby",
    "Magadan":"Asia/Magadan",
    "Solomon Is.":"Asia/Magadan",
    "New Caledonia":"Pacific/Noumea",
    "Fiji":"Pacific/Fiji",
    "Kamchatka":"Asia/Kamchatka",
    "Marshall Is.":"Pacific/Majuro",
    "Auckland":"Pacific/Auckland",
    "Wellington":"Pacific/Auckland",
    "Nuku'alofa":"Pacific/Tongatapu",
    "Tokelau Is.":"Pacific/Fakaofo",
    "Samoa":"Pacific/Apia"
}

# Filter for US timezones
# https://github.com/rails/rails/blob/master/activesupport/lib/active_support/values/time_zone.rb
US_Matcher = re.compile('US|Arizona|Indiana|Hawaii|Alaska')
def tz_in_us(humanName):
    return US_Matcher.search(humanName)

def human_timezones():
    return ruby_to_olson.keys()
    
def tz_code(humanTimezone):
    return ruby_to_olson[humanTimezone]
    
def tz(olsonCode):
    return pytz.timezone(olsonCode)

def valid_timezone(olsonCode):
    try:
        pytz.timezone(olsonCode)
        return True
    except UnknownTimeZoneError:
        return False
        
def tz_offset_string(delta):
    seconds = delta.total_seconds()
    minutes = seconds / 60
    hours = abs(math.floor(minutes / 60))
    minutes = abs(math.floor(minutes % 60))
    if seconds < 0:
        sign = '-'
    else:
        sign = '+'
        
    return "GMT%s%d:%02d" %(sign, hours, minutes)
    
def nice_tz_name(shortName, offset, humanTimezone=None):
    offset = tz_offset_string(offset)
    if humanTimezone:
        return "(%s) %s - %s" %(offset, humanTimezone, shortName)
    else:
        return '%s (%s)' %(shortName, offset)

    
def local_time(datetime_utc, local_tz):
    return local_tz.normalize(datetime_utc.astimezone(local_tz))
    