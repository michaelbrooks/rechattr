from sqlalchemy import Column, Table
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String, DateTime, BigInteger
from sqlalchemy.orm import relationship, backref    
from datetime import datetime

# Get the shared base class for declarative ORM
from . import Base
from decorators import UTCDateTime

poll_tweets = Table(
    'poll_tweets', 
    Base.metadata,
    Column('poll_id', Integer, ForeignKey('polls.id')),
    Column('tweet_id', BigInteger, ForeignKey('tweets.id'))
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
    