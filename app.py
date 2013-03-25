import web
import db, model
import appconfig as conf
import controllers
import migrate
from libs import AlchemyStore

# migrate the database before starting
migrate.migrate(conf.ALEMBIC_VERSION)

urls = (
    '/',                    'index',
    '/new',                 'create',
    '/clear_db',            'clear_db',
    '/sign_in',             'sign_in',
    '/([\w-]+)',            'poll',
    '/([\w-]+)/edit/(\w+)', 'edit',
    '/([\w-]+)/results',    'results'
)

web.config.debug = conf.DEBUG

web.config.session_parameters.cookie_name = 'rechattr_session_id'
web.config.session_parameters.secret_key = conf.SESSION_ENCRYPTION_KEY

app = web.application(urls, controllers.__dict__)

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
        # If the above alone doesn't work, uncomment 
        # the following line:
        #web.ctx.orm.expunge_all() 

def load_session(handler):
    sessionStore.set_db(web.ctx.orm)
    web.ctx.session = session
    
    return handler()
        
app.add_processor(load_sqla)
app.add_processor(load_session)

sessionStore = AlchemyStore()
session = web.session.Session(app, sessionStore)

app.notfound = controllers.notfound
app.add_processor(controllers.load_notfound)

if __name__ == "__main__":
    app.run()
