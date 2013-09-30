from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime, BigInteger
from sqlalchemy.orm import Session
from datetime import datetime
from dateutil.tz import tzoffset
import cPickle as pickle

# Get the shared base class for declarative ORM
import model
from utils import dtutils
from decorators import UTCDateTime

class User(model.Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    created = Column(UTCDateTime, default=datetime.utcnow)
    
    oauth_key = Column(String)

    oauth_user_id = Column(BigInteger)
    oauth_provider = Column(String)
    username = Column(String)
    full_name = Column(String)
    profile_image_url = Column(String)
    utc_offset = Column(Integer)
    human_timezone = Column(String)
    olson_timezone = Column(String)
    
    last_signed_in = Column(UTCDateTime, default=datetime.utcnow)
    tweet_count = Column(Integer, default=0)
    response_count = Column(Integer, default=0)
    
    user_cache = Column(String)
    
    def __init__(self, oauth_user_id, oauth_provider='Twitter'):
        self.oauth_user_id = oauth_user_id
        self.oauth_provider = oauth_provider
        
    def update(self, user_info, oauth_token):
        self.oauth_key = oauth_token.key
        
        self.user_cache = pickle.dumps(user_info)
        
        # retrieve some important fields from the user info
        if self.oauth_provider == "Twitter":
            self.username = user_info.screen_name
            self.full_name = user_info.name
            self.profile_image_url = user_info.profile_image_url_https
            self.utc_offset = user_info.utc_offset
            self.human_timezone = user_info.time_zone
            
            # if the timezone hasn't been set, try to guess it
            if self.olson_timezone is None:
                self.olson_timezone = self.guess_olson_timezone()
                
            
    def guess_olson_timezone(self):
        if self.human_timezone is not None and self.human_timezone in dtutils.ruby_to_olson:
            return dtutils.ruby_to_olson[self.human_timezone]
        
        return None

    def to_localtime(self, dt):
        if self.utc_offset is None:
            return dt
            
        tzinfo = tzoffset(self.time_zone, self.utc_offset);
        return dt.astimezone(tzinfo)
        
    def load_cache(self):
        return pickle.loads(self.user_cache.encode('utf-8'))

    def poll_stats(self, session, poll):
        tweetCount = session.query(model.Tweet).\
                             filter(model.Tweet.polls.contains(poll), 
                                    model.Tweet.user_id == self.oauth_user_id).\
                             count()
                             
        return {
            'tweets': tweetCount,
            'feedbacks': 0
        }

    def polls_by_start(self, session=None):
        if session is None:
            session = Session.object_session(self)
            
        return session.query(model.Poll).\
                       filter(model.Poll.user == self).\
                       order_by(model.Poll.event_start.desc()).\
                       all()

    def first_response(self, question):
        session = Session.object_session(self)

        return session.query(model.Response).\
                       filter(model.Response.user == self).\
                       filter(model.Response.question == question).\
                       first()