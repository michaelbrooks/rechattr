from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import relationship, backref
from datetime import datetime, timedelta
import simplejson as json
import time

# Get the shared base class for declarative ORM
from model import Base
from utils import utc_aware
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
    trigger_type = Column(String)
    trigger_info = Column(String)
    image_src = Column(String)
    question_text = Column(String)
    answer_choices = Column(String)

    def get_answer_choices(self):
        return json.loads(self.answers)
    
    def triggered(self):
        if self.trigger_type == 'time_offset':
            seconds = self.trigger_info
            trigger_delta = timedelta(0, seconds)
            
            start = self.poll.event_start
            now = utc_aware()
            delta = now - start
            
            return delta > trigger_delta
        elif self.trigger_type == 'manual':
            triggered = self.trigger_info
            return bool(triggered)
    
    def manual_trigger(self):
        if self.trigger_type != 'manual':
            raise Exception("Cannot manually trigger question with trigger type %s" %(self.trigger_type))
        
        # Record the time the manual trigger was activated
        self.trigger_info = time.time()
        