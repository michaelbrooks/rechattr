from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects import postgresql
from datetime import datetime

# Get the shared base class for declarative ORM
from model import Base
from decorators import UTCDateTime

class Visit(Base):
    __tablename__ = 'visits'
    
    id = Column(Integer, primary_key=True)
    created = Column(UTCDateTime, default=datetime.utcnow)
    
    poll_id = Column(Integer, ForeignKey('polls.id'))
    poll = relationship('Poll', 
                        backref=backref('visits', order_by=created))
                        
    url = Column(String)
    page = Column(String)
    ip_address = Column(postgresql.INET)
    device = Column(String)
    browser = Column(String)
