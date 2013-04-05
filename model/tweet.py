from sqlalchemy import Column, Table
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String, DateTime, BigInteger
from sqlalchemy.orm import relationship, backref    
from datetime import datetime

from dateutil import parser
import simplejson as json
from string import Template
from cgi import escape

from tweepy import Status

# Get the shared base class for declarative ORM
from model import Base
from utils.dtutils import utc_aware
from decorators import UTCDateTime

urlTemplate = Template('<a target="_blank" href="${url}" title="${expanded_url}">${display_url}</a>')
mentionTemplate = Template('<a target="_blank" href="https://twitter.com/${screen_name}" title="${name}">@${screen_name}</a>')
hashtagTemplate = Template('<a target="_blank" href="https://twitter.com/search?q=%23${text}">#${text}</a>')

def escape_dict(base, *args):
    result = dict()
    for kw in args:
        result[kw] = escape(base[kw])
    return result

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
    entities = Column(String)
    profile_image_url = Column(String)
    utc_offset = Column(Integer)
    
    # for saving parsed entities
    _json_entities = None
    
    def __init__(self, tweepyStatus):
        self.id = tweepyStatus.id
        self.created = tweepyStatus.created_at
        
        self.user_id = tweepyStatus.user.id
        self.screen_name = tweepyStatus.user.screen_name
        self.user_name = tweepyStatus.user.name
        self.profile_image_url = tweepyStatus.user.profile_image_url_https
        self.utc_offset = tweepyStatus.user.utc_offset
        
        self.text = tweepyStatus.text
        self.reply_to_tweet_id = tweepyStatus.in_reply_to_status_id
        
        self.entities = json.dumps(tweepyStatus.entities)
        
        if hasattr(tweepyStatus, 'retweet_of_status_id'):
            self.retweet_of_status_id = tweepyStatus.retweet_of_status_id
        
    
    @classmethod
    def fromJSON(cls, statusJson, tweepy):
        raise Exception("Does not work right now!")
        status = Status.parse(tweepy, statusJson)
        return cls(status)
    
    def get_entities(self):
        if self._json_entities is None:
            if self.entities is not None:
                self._json_entities = json.loads(self.entities)
                
        return self._json_entities
    
    def _prepare_entities(self):
        entities = self.get_entities()
        processed = list()
        
        if entities is None:
            return processed
            
        for url in entities['urls']:
            escaped = escape_dict(url, 'url', 'expanded_url', 'display_url')
            
            replacement = urlTemplate.substitute(escaped)
            indices = url['indices']
            
            processed.append((indices[0], indices[1], replacement))
            
        for mention in entities['user_mentions']:
            escaped = escape_dict(mention, 'screen_name', 'name')
            
            replacement = mentionTemplate.substitute(escaped)
            indices = mention['indices']
            
            processed.append((indices[0], indices[1], replacement))
            
        for hashtag in entities['hashtags']:
            escaped = escape_dict(hashtag, 'text')
            
            replacement = hashtagTemplate.substitute(escaped)
            indices = hashtag['indices']
            
            processed.append((indices[0], indices[1], replacement))
            
        # Now do mentions and hashtags also
        
        # now sort by start index (happens to be index 0)
        processed.sort()
        
        return processed
            
    def enriched_tweet_text(self):
        
        # get a list of (start, stop, replacement) tuples
        entities = self._prepare_entities()
        
        # a value to be modified as substrings are replaced
        offset = 0
        
        text = self.text
        for entity in entities:
            start = entity[0]
            end = entity[1] # exclusive
            replacement = entity[2]
            
            before = text[:start + offset]
            after = text[end + offset:]
            
            text = before + replacement + after
            offset += len(replacement) - (end - start)
            
        return text
            
    def created_timestamp(self):
        return dtutils.dt_timestamp(self.created)