from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime, BigInteger
from datetime import datetime
import cPickle as pickle

# Get the shared base class for declarative ORM
from model import Base, Tweet
from decorators import UTCDateTime

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    created = Column(UTCDateTime, default=datetime.utcnow)
    
    oauth_key = Column(String)
    oauth_secret = Column(String)
    
    oauth_user_id = Column(BigInteger)
    oauth_provider = Column(String)
    username = Column(String)
    full_name = Column(String)
    profile_image_url = Column(String)
    
    last_signed_in = Column(UTCDateTime, default=datetime.utcnow)
    tweet_count = Column(Integer, default=0)
    response_count = Column(Integer, default=0)
    
    user_cache = Column(String)
    
    def __init__(self, oauth_user_id, oauth_provider='Twitter'):
        self.oauth_user_id = oauth_user_id
        self.oauth_provider = oauth_provider
        
    def update(self, user_info, oauth_token):
        self.oauth_key = oauth_token.key
        self.oauth_secret = oauth_token.secret
        
        self.user_cache = pickle.dumps(user_info)
        
        # retrieve some important fields from the user info
        if self.oauth_provider == "Twitter":
            self.username = user_info.screen_name
            self.full_name = user_info.name
            self.profile_image_url = user_info.profile_image_url_https

    def load_cache(self):
        return pickle.loads(self.user_cache.encode('utf-8'))

    def poll_stats(self, session, poll):
        tweetCount = session.query(Tweet).\
                             filter(Tweet.polls.contains(poll), Tweet.user_id == self.oauth_user_id).\
                             count()
                             
        return {
            'tweets': tweetCount,
            'feedbacks': 0
        }