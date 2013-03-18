import web
import db, model
import appconfig as conf
import controllers

urls = (
    '/',                    'index',
    '/new',                 'create',
    '/clear_db',            'clear_db',
    '/([\w-]+)',               'poll',
    '/([\w-]+)/edit/(\w+)',    'edit',
    '/([\w-]+)/results',       'results'
)

web.config.debug = conf.DEBUG

app = web.application(urls, globals())

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


app.add_processor(load_sqla)

app.notfound = controllers.notfound
app.add_processor(controllers.load_notfound)

from controllers import *

if __name__ == "__main__":
    app.run()
