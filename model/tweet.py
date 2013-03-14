from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String, DateTime, BigInteger
from sqlalchemy.orm import relationship, backref    
from datetime import datetime

# Get the shared base class for declarative ORM
from . import Base
    
class Tweet(Base):
    __tablename__ = 'tweets'
    
    id = Column(BigInteger, primary_key=True)
    created = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    poll_id = Column(Integer, ForeignKey('polls.id'))
    poll = relationship('Poll', 
                        backref=backref('tweets', order_by=created))
                        
    user_id = Column(BigInteger)
    screen_name = Column(String)
    user_name = Column(String)
    text = Column(String)
    retweet_of_status_id = Column(BigInteger)
    reply_to_tweet_id = Column(BigInteger)
    