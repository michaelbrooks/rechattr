from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import relationship, backref

# Get the shared base class for declarative ORM
from . import Base

class Response(Base):
    __tablename__ = 'responses'
    
    id = Column(Integer, primary_key=True)
    created = Column(DateTime(timezone=True))
    
    poll_id = Column(Integer, ForeignKey('polls.id'))
    poll = relationship('Poll', 
                        backref=backref('responses', order_by=created))
    
    visit_id = Column(Integer, ForeignKey('visits.id'))
    visit = relationship('Visit', 
                         uselist=False,
                         backref=backref('response', uselist=False))
    
    answers = Column(String)
    comment = Column(String)
