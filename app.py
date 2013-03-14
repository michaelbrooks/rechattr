import web
import db, model
import appconfig as conf
import controllers

urls = (
    '/',                    'index',
    '/new',                 'create',
    '/r(\w+)/edit/(\w+)',   'edit',
    '/r(\w+)',              'poll',
    '/r(\w+)/results',      'results'
)

web.config.debug = conf.DEBUG

app = web.application(urls, globals())
app.add_processor(db.load_sqla)
app.add_processor(controllers.load_notfound)

from controllers import *

if __name__ == "__main__":
    app.run()
