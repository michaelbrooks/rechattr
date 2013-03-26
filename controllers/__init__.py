import web

helpers = {
    'web': web
}

render = web.template.render('templates/', globals=helpers)
pagerender = web.template.render('templates/', base='layout', globals=helpers)


from create import create
from edit import edit
from poll import poll
from results import results
from index import index
from clear_db import clear_db
from sign_in import sign_in

def notfound():
    return web.notfound(render.notfound())

def load_notfound(handler):
    web.ctx.notfound = notfound
    return handler()