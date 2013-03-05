from sqlalchemy import create_engine
import appconfig as conf

# Connect to the database    
engine = create_engine(conf.DATABASE_URL, echo=conf.DEBUG)
