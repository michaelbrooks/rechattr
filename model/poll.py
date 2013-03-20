from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime
from datetime import datetime
import simplejson as json

# Get the shared base class for declarative ORM
from . import Base
from decorators import UTCDateTime

class Poll(Base):
    __tablename__ = 'polls'
    
    POLL_URL_CODE_LENGTH = 6
    RESULTS_URL_CODE_LENGTH = 10
    EDIT_URL_CODE_LENGTH = 10
    
    # Record info
    id = Column(Integer, primary_key=True)
    created = Column(UTCDateTime, default=datetime.utcnow)
    updated = Column(UTCDateTime, default=datetime.utcnow)
    
    #User info
    user_email = Column(String)
    
    # Event info
    title = Column(String)
    event_start = Column(UTCDateTime)
    event_stop = Column(UTCDateTime)
    twitter_user = Column(String)
    twitter_hashtag = Column(String)
    twitter_other_terms = Column(String)
    
    # Urls
    poll_url_code = Column(String)
    results_url_code = Column(String)
    edit_url_code = Column(String)
    poll_short_url = Column(String)
    
    #The poll definition, json
    definition = Column(String)

    def results_url(self):
        return '/%s/results' % (self.poll_url_code)
    
    def poll_url(self):
        return '/%s' % (self.poll_url_code)
        
    def edit_url(self):
        return '/%s/edit/%s' % (self.poll_url_code, self.edit_url_code)
        
    def definition_object(self):
        return json.loads(self.definition)
    
    def twitter_other_terms_list(self):
        if self.twitter_other_terms is not None:
            return self.twitter_other_terms.split(',')
        else:
            return []
            
    def twitter_track_list(self):
        
        # track_list = self.twitter_other_terms_list()
        return [self.twitter_user.lower(), self.twitter_hashtag.lower()]
    
    @staticmethod
    def get_active(session):
        # Check the database for events that are happening right now
        now = datetime.utcnow()
        
        return session.query(Poll).\
                       filter(Poll.event_start <= now, Poll.event_stop >= now).\
                       all()