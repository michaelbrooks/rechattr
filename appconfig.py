import os, random, hashlib, time

# Get the database connection url
DATABASE_URL = os.environ.get('DATABASE_URL', None)
if DATABASE_URL == None:
    error("DATABASE_URL not in environment")
    exit(1)

DEBUG = bool(os.environ.get('DEBUG', False))
DEBUG_SERVER_PORT = os.environ.get('DEBUG_SERVER_PORT', 9999)
DEBUG_SERVER_HOST = os.environ.get('DEBUG_SERVER_HOST', 'localhost')

DB_DEBUG = bool(os.environ.get('DB_DEBUG', False))
LOG_LEVEL = bool(os.environ.get('LOG_LEVEL', 'INFO' if DEBUG else 'ERROR'))

STATIC_ROOT = os.environ.get('STATIC_ROOT', '/static');
DEVELOPMENT_ASSETS = bool(os.environ.get('DEVELOPMENT_ASSETS', False))

TWITTER_STREAM_CONSUMER_KEY = os.environ.get('TWITTER_STREAM_CONSUMER_KEY', None)
TWITTER_STREAM_CONSUMER_SECRET = os.environ.get('TWITTER_STREAM_CONSUMER_SECRET', None)
TWITTER_STREAM_ACCESS_KEY = os.environ.get('TWITTER_STREAM_ACCESS_KEY', None)
TWITTER_STREAM_ACCESS_SECRET = os.environ.get('TWITTER_STREAM_ACCESS_SECRET', None)

STREAM_TERM_POLLING_INTERVAL = int(os.environ.get('STREAM_TERM_POLLING_INTERVAL', 60))

ALEMBIC_VERSION = os.environ.get('ALEMBIC_VERSION', 'head')

_default_key = hashlib.sha1("%s%s" %(random.random(), time.time())).hexdigest()
SESSION_ENCRYPTION_KEY = os.environ.get('SESSION_ENCRYPTION_KEY', _default_key)
