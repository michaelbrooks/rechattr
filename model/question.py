from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String, Boolean, Float
from sqlalchemy.orm import relationship, backref
from datetime import datetime, timedelta
import simplejson as json
import time

# Get the shared base class for declarative ORM
from model import Base
from utils import dtutils
from utils.dtutils import utc_aware
from decorators import UTCDateTime

class Question(Base):
    __tablename__ = 'questions'
    
    # Record info
    id = Column(Integer, primary_key=True)
    created = Column(UTCDateTime, default=datetime.utcnow)
    
    #Poll info
    poll_id = Column(Integer, ForeignKey('polls.id'))
    poll = relationship('Poll',
                        backref=backref('questions', order_by=created))
    
    # Question info
    trigger_manual = Column(Boolean, default=False)
    trigger_seconds = Column(Float, default=None)
    image_src = Column(String)
    subject = Column(String)
    question_text = Column(String)
    answer_choices = Column(String)

    def get_answer_choices(self):
        if not hasattr(self, '_cached_answers'):
            self._cached_answers = json.loads(self.answer_choices)
        return self._cached_answers
        
    def set_answer_choices(self, answers):
        self.answer_choices = json.dumps(answers)
        self._cached_answers = answers
        
    def percent_through_event(self):
        """
        Get the percent through the event when this question
        is triggered. If there is no trigger time, this will return None.

        :return:
        """
        if self.trigger_seconds is None:
            return None
        duration = self.poll.duration().total_seconds()
        return self.trigger_seconds / duration;
        
    def nice_offset(self):
        if self.trigger_seconds is None:
            return None

        delta = timedelta(seconds=self.trigger_seconds)
        return dtutils.nice_delta(delta, sub=True)
        
    def triggered(self):
        # see if manually triggered first
        if self.trigger_manual:
            return True

        # then see if time triggered
        if self.trigger_seconds is not None:
            seconds = self.trigger_seconds
            trigger_delta = timedelta(0, seconds)
            
            start = self.poll.event_start
            now = utc_aware()
            delta = now - start
            
            return delta > trigger_delta

        return False

    def get_time(self):
        if self.trigger_seconds is None:
            return None

        offset_delta = timedelta(seconds=self.trigger_seconds)
        return self.poll.event_start + offset_delta

    def manual_trigger(self):
        # Mark the question as triggered manually
        self.trigger_manual = True

        # Record the time offset against the poll start, in seconds
        offset_delta = (utc_aware() - self.poll.event_start)
        self.trigger_seconds = offset_delta.total_seconds()
        