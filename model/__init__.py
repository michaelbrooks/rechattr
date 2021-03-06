from sqlalchemy.ext.declarative import declarative_base

## http://docs.sqlalchemy.org/en/rel_0_8/orm/tutorial.html
# Base class for declarative ORM classes
Base = declarative_base()

# Load all of the models into the package
from tweet import Tweet
from response import Response
from visit import Visit
from user import User
from session import Session
from question import Question
from poll import Poll