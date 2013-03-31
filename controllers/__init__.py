import web, time, calendar

helpers = {
    'web': web,
    'time': time,
    'calendar': calendar
}

render = web.template.render('templates/', globals=helpers)
pagerender = web.template.render('templates/', base='layout', globals=helpers)
elements = web.template.render('templates/elements', globals=helpers)

helpers['elements'] = elements

from model import Tweet
def render_stream_item(item, newItem=False):
    itemType = type(item)
    if itemType is Tweet:
        return elements.tweet(item, newItem)

helpers['render_stream_item'] = render_stream_item

from create import create
from edit import edit
from poll import poll
from results import results
from index import index
from clear_db import clear_db
from sign_in import sign_in
from stream import stream

def notfound():
    return web.notfound(render.notfound())

def load_notfound(handler):
    web.ctx.notfound = notfound
    return handler()