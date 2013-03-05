import os
from sqlalchemy import create_engine

# Get the database connection url
DATABASE_URL = os.environ.get('DATABASE_URL', None)
if DATABASE_URL == None:
    print "DATABASE_URL not in environment"
    
# Connect to the database    
engine = create_engine(DATABASE_URL, echo=True)
