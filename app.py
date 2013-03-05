import web
import db, model
import appconfig as conf

urls = (
    '/',                    'index',
    '/new',                 'create',
    '/r(\w+)/edit/(\w+)',   'edit',
    '/r(\w+)/poll',         'poll',
    '/r(\w+)',              'results'
)

web.config.debug = conf.DEBUG

app = web.application(urls, globals())
app.add_processor(db.load_sqla)

from controllers import *

if __name__ == "__main__":
    app.run()
