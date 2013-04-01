import web, time, calendar
from urllib import urlencode

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
from welcome import welcome
from clear_db import clear_db
from sign_in import sign_in
from stream import stream

def notfound():
    return web.notfound(render.notfound())

def load_notfound(handler):
    web.ctx.notfound = notfound
    return handler()

class AppUrls(object):
    
    urls = (
        '/',                    'welcome',
        '/polls',               'index',
        '/new',                 'create',
        '/clear_db',            'clear_db',
        '/sign_in',             'sign_in',
        '/sign_out',            'sign_in',
        '/([\w-]+)',            'poll',
        '/([\w-]+)/edit/(\w+)', 'edit',
        '/([\w-]+)/stream',     'stream',
        '/([\w-]+)/results',    'results'
    )
    
    controller_map = {
        'welcome': welcome,
        'index': index,
        'create': create,
        'clear_db': clear_db,
        'sign_in': sign_in,
        'poll': poll,
        'edit': edit,
        'stream': stream,
        'results': results
    }
    
    def home(self):
        return '/'
    
    def sign_in(self, return_to=None):
        if return_to is None:
            return_to = self.home()
            
        return '/sign_in?%s' %(urlencode({'return_to': return_to}))

    def poll_results(self, poll):
        return '/%s/results' % (poll.poll_url_human)
    
    def poll(self, poll):
        return '/%s' % (poll.poll_url_human)
        
    def poll_edit(self, poll):
        return '/%s/edit/%s' % (poll.poll_url_human, poll.edit_url_code)

    def polls_list(self):
        return '/polls'
    
    def new_poll(self):
        return '/new'
        
    def sign_out(self):
        return '/sign_out'
        
urls = AppUrls()

helpers['urls'] = urls