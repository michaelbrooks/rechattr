from sqlalchemy import Column
from sqlalchemy import String
from datetime import datetime

# Get the shared base class for declarative ORM
from model import Base
from decorators import UTCDateTime

class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(String(128), primary_key=True)
    atime = Column(UTCDateTime, default=datetime.utcnow)
    data = Column(String)
    
    def __init__(self, id, data):
        self.id = id
        self.data = data
