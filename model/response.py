from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import relationship, backref
from datetime import datetime

# Get the shared base class for declarative ORM
from model import Base
from decorators import UTCDateTime

class Response(Base):
    __tablename__ = 'responses'
    
    id = Column(Integer, primary_key=True)
    created = Column(UTCDateTime, default=datetime.utcnow)
    
    poll_id = Column(Integer, ForeignKey('polls.id'))
    poll = relationship('Poll', 
                        backref=backref('responses', order_by=created))
    
    visit_id = Column(Integer, ForeignKey('visits.id'))
    visit = relationship('Visit', 
                         uselist=False,
                         backref=backref('response', uselist=False))
    
    answers = Column(String)
    comment = Column(String)
