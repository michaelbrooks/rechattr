from sqlalchemy.ext.declarative import declarative_base

## http://docs.sqlalchemy.org/en/rel_0_8/orm/tutorial.html
# Base class for declarative ORM classes
Base = declarative_base()

from dateutil.tz import tzoffset, tzutc
utc = tzutc()

# Forces a datetime into utc
def utc_aware(dt):
    return dt.replace(tzinfo=utc)

# Load all of the models into the package
from poll import Poll
from tweet import Tweet
from response import Response
from visit import Visit
from user import User
from session import Session