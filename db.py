from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import appconfig as conf

# Connect to the database    
engine = create_engine(conf.DATABASE_URL, echo=conf.DB_DEBUG)

def db_session():
    return scoped_session(sessionmaker(bind=engine))
