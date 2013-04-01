from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import relationship, backref
from datetime import datetime
import simplejson as json

# Get the shared base class for declarative ORM
from model import Base, Tweet
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
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', 
                        backref=backref('polls', order_by=created))
    email = Column(String)
    
    # Event info
    title = Column(String)
    event_start = Column(UTCDateTime)
    event_stop = Column(UTCDateTime)
    twitter_hashtag = Column(String)
    twitter_other_terms = Column(String)
    
    # Urls
    poll_url_human = Column(String)
    poll_url_code = Column(String)
    results_url_code = Column(String)
    edit_url_code = Column(String)
    poll_short_url = Column(String)
    
    #The poll definition, json
    definition = Column(String)

    def definition_object(self):
        return json.loads(self.definition)
    
    def twitter_other_terms_list(self):
        if self.twitter_other_terms is not None:
            return self.twitter_other_terms.split(',')
        else:
            return []
            
    def twitter_track_list(self):
        
        return ['@%s'%(self.user.username.lower()), self.twitter_hashtag.lower()]
    
    def tweet_stream(self, session):
        query = session.query(Tweet).\
                        filter(Tweet.polls.contains(self)).\
                        order_by(Tweet.created.desc())
        return query.all()
    
    @staticmethod
    def get_active(session):
        # Check the database for events that are happening right now
        now = datetime.utcnow()
        
        #TODO: add buffer to beginning and end
        return session.query(Poll).\
                       filter(Poll.event_start <= now, Poll.event_stop >= now).\
                       all()
    @staticmethod
    def get_by_url(session, poll_url_code):
        return session.query(Poll).\
                       filter(Poll.poll_url_code == poll_url_code.lower()).\
                       first()