import web

render = web.template.render('templates/')
pagerender = web.template.render('templates/', base='layout')


from create import create
from edit import edit
from poll import poll
from results import results
from index import index

def notfound():
    return web.notfound(render.notfound())

def load_notfound(handler):
    web.ctx.notfound = notfound
    return handler()