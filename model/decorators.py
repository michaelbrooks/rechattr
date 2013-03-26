# from http://stackoverflow.com/questions/2528189/can-sqlalchemy-datetime-objects-only-be-naive

from sqlalchemy import types
from dateutil.tz import tzutc
from datetime import datetime

utc = tzutc()

class UTCDateTime(types.TypeDecorator):

    impl = types.DateTime

    def process_bind_param(self, value, engine):
        if value is not None:
            if value.tzinfo is None:
                return value.replace(tzinfo=utc)
            else:
                return value.astimezone(utc)

    def process_result_value(self, value, engine):
        if value is not None:
            if value.tzinfo is None:
                return value.replace(tzinfo=utc)
            else:
                return value.astimezone(utc)