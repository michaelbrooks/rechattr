from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime

# Get the shared base class for declarative ORM
from . import Base

class Poll(Base):
    __tablename__ = 'polls'
    
    # Record info
    id = Column(Integer, primary_key=True)
    created = Column(DateTime(timezone=True))
    updated = Column(DateTime(timezone=True))
    
    #User info
    user_email = Column(String)
    
    # Event info
    event_start = Column(DateTime(timezone=True))
    event_stop = Column(DateTime(timezone=True))
    twitter_terms = Column(String)
    
    # Urls
    poll_url_code = Column(String)
    results_url_code = Column(String)
    edit_url_code = Column(String)
    poll_short_url = Column(String)
    
    #The poll definition, json
    definition = Column(String)
    