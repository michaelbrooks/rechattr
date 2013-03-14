from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime
from datetime import datetime
import simplejson as json

# Get the shared base class for declarative ORM
from . import Base

class Poll(Base):
    __tablename__ = 'polls'
    
    POLL_URL_CODE_LENGTH = 6
    RESULTS_URL_CODE_LENGTH = 10
    EDIT_URL_CODE_LENGTH = 10
    
    # Record info
    id = Column(Integer, primary_key=True)
    created = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated = Column(DateTime(timezone=True), default=datetime.utcnow)
    
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

    def results_url(self):
        return '/r%s/results' % (self.poll_url_code)
    
    def poll_url(self):
        return '/r%s' % (self.poll_url_code)
        
    def edit_url(self):
        return '/r%s/edit/%s' % (self.poll_url_code, self.edit_url_code)
        
    def definition_object(self):
        return json.loads(self.definition)