import web
import db, model
import appconfig as conf
import controllers
import migrate
import utils
from utils.auth import Auth
from utils.alchemystore import AlchemyStore
from utils.flash import Flash
from utils.logger import Logger

# migrate the database before starting
migrate.migrate(conf.ALEMBIC_VERSION)

web.config.debug = conf.DEBUG

if conf.DEBUG:
    try:
        import pydevd
        pydevd.settrace(conf.DEBUG_SERVER_HOST, port=conf.DEBUG_SERVER_PORT, stdoutToServer=True, stderrToServer=True, suspend=False)
    except ImportError:
        print 'ERROR: Unable to import pydevd for remote debugging!'
    except:
        print 'ERROR: Could not connect to remote debugging server'

web.config.session_parameters.cookie_name = 'rechattr_session_id'
web.config.session_parameters.secret_key = conf.SESSION_ENCRYPTION_KEY

from controllers import urls
app = web.application(urls.urls, urls.controller_map)

# entry point for wsgi servers
# http://stackoverflow.com/questions/13667103/web-py-and-gunicorn
wsgi_app = app.wsgifunc()

def load_sqla(handler):
    web.ctx.orm = db.db_session()
    
    try:
        return handler()
    except web.HTTPError:
        web.ctx.orm.commit()
        raise
    except:
        web.ctx.orm.rollback()
        raise
    finally:
        web.ctx.orm.commit()
        # web.ctx.orm.expunge_all() 

def load_session(handler):
    # make the url manager available
    web.ctx.urls = urls
    
    # provide a convenient way to return json data
    web.ctx.json = utils.json
    
    # set up the session
    sessionStore.set_db(web.ctx.orm)
    web.ctx.session = session
    
    # set up the flash util
    web.ctx.flash = Flash()
    
    # Set up for oauth
    consumer_token = conf.TWITTER_STREAM_CONSUMER_KEY
    consumer_secret = conf.TWITTER_STREAM_CONSUMER_SECRET
    web.ctx.auth = Auth(consumer_token, consumer_secret)

    # Set up the logger
    web.ctx.log = Logger()
    
    return handler()
        
app.add_processor(load_sqla)
app.add_processor(load_session)

sessionStore = AlchemyStore()
session = web.session.Session(app, sessionStore)

app.notfound = controllers.notfound
app.add_processor(controllers.load_notfound)

if __name__ == "__main__":
    import sys, os
    from web.utils import listget, intget
    from web.net import validaddr, validip

    server = None
    def runsimple(func, server_address=("0.0.0.0", 8080)):
        """
        Runs [CherryPy][cp] WSGI server hosting WSGI app `func`.
        The directory `static/` is hosted statically.

        [cp]: http://www.cherrypy.org
        """
        global server
        func = web.httpserver.StaticMiddleware(func, conf.STATIC_ROOT) #This is the whole point of these shenanigans
        func = web.httpserver.LogMiddleware(func)

        server = web.httpserver.WSGIServer(server_address, func)

        if server.ssl_adapter:
            print "https://%s:%d/" % server_address
        else:
            print "http://%s:%d/" % server_address

        try:
            server.start()
        except (KeyboardInterrupt, SystemExit):
            server.stop()
            server = None


    server_addr = validip(listget(sys.argv, 1, ''))
    if os.environ.has_key('PORT'): # e.g. Heroku
        server_addr = ('0.0.0.0', intget(os.environ['PORT']))

    runsimple(wsgi_app, server_addr)
