from sqlalchemy import Column, Table
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String, DateTime, BigInteger
from sqlalchemy.orm import relationship, backref    
from datetime import datetime
from dateutil import parser

# Get the shared base class for declarative ORM
from . import Base
from decorators import UTCDateTime

poll_tweets = Table(
    'poll_tweets', 
    Base.metadata,
    Column('poll_id', Integer, ForeignKey('polls.id'), nullable=False),
    Column('tweet_id', BigInteger, ForeignKey('tweets.id'), nullable=False)
)

class Tweet(Base):
    __tablename__ = 'tweets'
    
    id = Column(BigInteger, primary_key=True)
    created = Column(UTCDateTime, default=datetime.utcnow)
    
    polls = relationship('Poll', 
                         secondary='poll_tweets',
                         backref=backref('tweets', order_by=created))
                        
    user_id = Column(BigInteger)
    screen_name = Column(String)
    user_name = Column(String)
    text = Column(String)
    retweet_of_status_id = Column(BigInteger)
    reply_to_tweet_id = Column(BigInteger)
    
    def __init__(self, status_obj):
        self.id = status_obj['id']
        self.created = parser.parse(status_obj['created_at'])
        self.user_id = status_obj['user']['id']
        self.screen_name = status_obj['user']['screen_name']
        self.user_name = status_obj['user']['name']
        self.text = status_obj['text']
        self.reply_to_tweet_id = status_obj['in_reply_to_status_id']
        if 'retweet_of_status_obj_id' in status_obj:
            self.retweet_of_status_obj_id = status_obj['retweet_of_status_id']
    