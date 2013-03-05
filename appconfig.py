import os

# Get the database connection url
DATABASE_URL = os.environ.get('DATABASE_URL', None)
if DATABASE_URL == None:
    error("DATABASE_URL not in environment")
    exit(1)

DEBUG = True if os.environ.get('DEBUG', False) else False
