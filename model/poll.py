from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String, BigInteger
from sqlalchemy.orm import relationship, backref, Session

from datetime import datetime, timedelta

# Get the shared base class for declarative ORM
import model
from utils.dtutils import utc_aware
from utils import dtutils
from decorators import UTCDateTime
from sqlalchemy import func

from string import Template
poll_tweet_template = Template('${title} is starting with official hashtag ${hashtag} on @rechattr ${link}')

class Poll(model.Base):
    __tablename__ = 'polls'
    
    POLL_URL_CODE_LENGTH = 6
    
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
    absolute_url = Column(String)

    announcement_tweet_id = Column(BigInteger, ForeignKey('tweets.id'), default=None)
    announcement_tweet = relationship('Tweet',
                                      backref=backref('poll_announced',
                                                      uselist=False))

    def can_tweet(self):
        return self.user.can_tweet()

    def post_tweet(self, api):

        text = poll_tweet_template.substitute(
            title=self.title,
            hashtag=self.twitter_hashtag,
            link=self.absolute_url
        )

        tweet = self.user.post_tweet(text, api=api)
        if tweet:
            self.announcement_tweet = tweet
            tweet.polls.append(self)

            return tweet

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

    def sorted_questions(self, session=None):
        if session is None:
            session = Session.object_session(self)

        query = session.query(model.Question). \
            filter(model.Question.poll == self)

        query = query.order_by(model.Question.trigger_seconds.desc())

        return query.all()

    # Gets the number of time each answer was chosen, for each question
    def get_question_responses(self, session = None):
        if session is None:
            session = Session.object_session(self)

        #shortcut
        Response = model.Response

        query = session.query(Response.question_id, Response.answer, func.count(Response.id)).\
                        filter(Response.poll == self).\
                        group_by(Response.question_id, Response.answer)

        result = dict()
        for question_id, answer, count in query.all():
            if question_id not in result:
                result[question_id] = dict()

            question = result[question_id]

            question[answer] = count

        return result

    def triggered_questions(self, session=None, limit=10, older_than=None, newer_than=None, untweeted_only=False):

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

        if untweeted_only:
            query = query.filter(model.Question.announcement_tweet_id == None)

        # Conditions for select
        query = query.order_by(model.Question.trigger_seconds.desc())\

        if limit is not None:
            query = query.limit(limit)

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
        
    def iso_event_start(self):

        tzone = dtutils.tz(self.olson_timezone)
        local_start = dtutils.local_time(self.event_start, tzone)

        return local_start.isoformat();

    def nice_local_interval(self):
        tzone = dtutils.tz(self.olson_timezone)
        local_start = dtutils.local_time(self.event_start, tzone)
        local_stop = dtutils.local_time(self.event_stop, tzone)

        return dtutils.nice_interval(local_start, local_stop)


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
    def get_active(session, untweeted_only=False):
        # Check the database for events that are happening right now
        now = datetime.utcnow()
        
        #TODO: add buffer to beginning and end
        query = session.query(Poll).\
                        filter(Poll.event_start <= now, Poll.event_stop >= now);

        if untweeted_only:
            query = query.filter(Poll.announcement_tweet_id is None)

        return query.all()

    @staticmethod
    def get_by_url(session, poll_url_code):
        return session.query(Poll).\
                       filter(Poll.poll_url_code == poll_url_code.lower()).\
                       first()

    @staticmethod
    def clean_term(term, prefix):
        term = term.strip()
        if term.startswith(prefix):
            return term
        return "%s%s" %(prefix, term)