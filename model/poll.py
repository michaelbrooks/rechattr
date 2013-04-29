from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import relationship, backref, Session

from datetime import datetime, timedelta
import simplejson as json

# Get the shared base class for declarative ORM
import model
from utils.dtutils import utc_aware
from decorators import UTCDateTime

class Poll(model.Base):
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
    olson_timezone = Column(String)
    
    twitter_hashtag = Column(String)
    twitter_other_terms = Column(String)
    
    # Urls
    poll_url_human = Column(String)
    poll_url_code = Column(String)
    results_url_code = Column(String)
    edit_url_code = Column(String)
    poll_short_url = Column(String)
    
    def twitter_other_terms_list(self):
        if self.twitter_other_terms is not None:
            return self.twitter_other_terms.split(',')
        else:
            return []
            
    def twitter_track_list(self):
        
        return ['@%s'%(self.user.username.lower()), self.twitter_hashtag.lower()]
    
    def count_tweets(self, session=None):
        if session is None:
            session = Session.object_session(self)
        
        return session.query(model.Tweet).\
                       filter(model.Tweet.polls.contains(self)).\
                       count()
    
    def count_responses(self, session=None):
        if session is None:
            session = Session.object_session(self)
        
        return session.query(model.Response).\
                       filter(model.Response.poll ==self).\
                       count()
    
    def tweet_stream(self, session=None, limit=10, older_than=None, newer_than=None):
        if session is None:
            session = Session.object_session(self)

        query = session.query(model.Tweet).\
                        filter(model.Tweet.polls.contains(self)).\
                        filter(model.Tweet.retweet_of_status_id == None)
                        # return no retweets
        
        if older_than:
            query = query.filter(model.Tweet.created < older_than)
        if newer_than:
            query = query.filter(model.Tweet.created > newer_than)

        query = query.order_by(model.Tweet.created.desc()).\
                      limit(limit)

        return query.all()

    def triggered_questions(self, session=None, limit=10, older_than=None, newer_than=None):

        if older_than is None:
            older_than = utc_aware()

        if session is None:
            session = Session.object_session(self)

        query = session.query(model.Question).\
                        filter(model.Question.poll == self)

        # make sure it is an active question
        current_offset = (utc_aware() - self.event_start).total_seconds()
        current_offset = model.Question.trigger_seconds < current_offset
        manuallyTriggered = model.Question.trigger_manual == True
        query = query.filter(manuallyTriggered | current_offset)

        if older_than:
            # convert the older_than into an offset against the event start
            older_than_offset = (older_than - self.event_start).total_seconds()
            older_than_offset = model.Question.trigger_seconds < older_than_offset
            query = query.filter(older_than_offset)

        if newer_than:
            # convert the newer_than into an offset against the event start
            newer_than_offset = (newer_than - self.event_start).total_seconds()
            query = query.filter(model.Question.trigger_seconds > newer_than_offset)

        # Conditions for select
        query = query.order_by(model.Question.trigger_seconds.desc()).\
                      limit(limit)

        return query.all()

    def get_stream(self, session=None, limit=10, older_than=None, newer_than=None):
        if older_than is None:
            older_than = utc_aware()

        tweets = self.tweet_stream(limit=limit, older_than=older_than, newer_than=newer_than)
        questions = self.triggered_questions(limit=limit, older_than=older_than, newer_than=newer_than)

        # merge the two lists, up to the limit
        merged = []
        tweet_cursor = 0
        question_cursor = 0
        while len(merged) < limit:

            next_tweet = None
            if tweet_cursor < len(tweets):
                next_tweet = tweets[tweet_cursor]

            next_question = None
            if question_cursor < len(questions):
                next_question = questions[question_cursor]

            if next_tweet and next_question:
                # compare to see which is newer
                if next_question.get_time() > next_tweet.get_time():
                    # the question was newer, so nullify the tweet and drop through
                    next_tweet = None
                else:
                    # the tweet was newer, so nullify the question and drop through
                    next_question = None

            if next_tweet:
                # use the tweet
                tweet_cursor += 1
                merged.append(next_tweet)
                continue

            if next_question:
                # use the question
                question_cursor += 1
                merged.append(next_question)
                continue

            # we have run out of both if we get this far
            break

        return merged

    def has_started(self):
        now = utc_aware()
        return now > self.event_start
        
    def is_active(self):
        now = utc_aware()
        return now > self.event_start and now < self.event_stop
    
    def has_ended(self):
        now = utc_aware()
        return now > self.event_stop
    
    def duration(self):
        return self.event_stop - self.event_start
        
    
    @classmethod
    def date_format(cls, dt, withDate=True, tz=None):
        if tz is not None:
            dt = dt.astimezone(tz)
            
        str = dt.strftime('%I:%M%p').lstrip('0').lower()
        if withDate:
            day = dt.strftime('%d').lstrip('0')
            str += dt.strftime(', %B ' + day + ' %Y')
           
        offset = dt.utcoffset()
        if offset is not None and offset.total_seconds() == 0:
            str += ' UTC'
            
        return str
    
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