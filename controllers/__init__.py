import web, time
from urllib import urlencode
import utils
import appconfig

static_file_versions = appconfig.static_file_versions()

def static_file(path):
    if path in static_file_versions:
        path = "%s?v=%s" %(path, static_file_versions[path])

    return appconfig.STATIC_ROOT + path

helpers = {
    'web': web,
    'time': time,
    'getattr': getattr,
    'round': round,
    'sum': sum,
    'dtutils': utils.dtutils,
    'csrf_token_input': utils.csrf_token_input,
    'app_context': appconfig.APP_ENVIRONMENT,
    'static_file': static_file,
    'ga': {
        'id': appconfig.GOOGLE_ANALYTICS_ID,
        'domain': appconfig.GOOGLE_ANALYTICS_DOMAIN
    },
    'campaigns': appconfig.CAMPAIGN_MODES
}

render = web.template.render('templates/', globals=helpers)
pagerender = web.template.render('templates/', base='layout', globals=helpers)
elements = web.template.render('templates/elements', globals=helpers)

helpers['elements'] = elements

from model import Tweet, Question
def render_stream_item(item, newItem=False, highlight=False):
    itemType = type(item)
    if itemType is Tweet:
        return elements.tweet(item, newItem, highlight)
    elif itemType is Question:
        return elements.question(item, newItem, highlight)

helpers['render_stream_item'] = render_stream_item

from create import create
from edit import edit
from poll import poll
from results import results
from myevents import myevents
from question import question
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
        '/events',              'myevents',
        '/new',                 'create',
        '/sign_in',             'sign_in',
        '/sign_out',            'sign_in',
        '/([\w-]+)',            'poll',
        '/([\w-]+)/(tweet)',      'poll', # for posting new tweets
        '/([\w-]+)/(answer)',     'poll', # for answering questions
        '/([\w-]+)/edit',             'edit',
        '/([\w-]+)/edit/(\w+)/(\d*)', 'edit', #REST
        '/([\w-]+)/questions',        'question', #REST
        '/([\w-]+)/questions/',        'question', #REST
        '/([\w-]+)/questions/(\d+)',  'question', #REST
        '/([\w-]+)/stream',     'stream',
        '/([\w-]+)/results',    'results'
    )
    
    controller_map = {
        'welcome': welcome,
        'myevents': myevents,
        'create': create,
        'clear_db': clear_db,
        'sign_in': sign_in,
        'poll': poll,
        'edit': edit,
        'stream': stream,
        'question': question,
        'results': results
    }
    
    def absolute(self, url):
        return web.ctx.home + url

    def requested(self):
        return web.ctx.path
        
    def home(self):
        return '/'
    
    def sign_in(self, return_to=None):
        if return_to is None:
            return_to = web.ctx.fullpath
            
        return '/sign_in?%s' %(urlencode({'return_to': return_to}))

    def poll_results(self, poll):
        return '/%s/results' % (poll.poll_url_human)
    
    def poll(self, poll):
        return '/%s' % (poll.poll_url_human)
        
    def poll_edit(self, poll):
        return '/%s/edit' % (poll.poll_url_human)
    
    def poll_delete(self, poll):
        return '/events/%s/delete' % (poll.poll_url_human)
        
    def polls_list(self):
        return '/events'
    
    def new_poll(self):
        return '/new'
        
    def sign_out(self):
        return '/sign_out'
    
    def twitter_hashtag(self, hashtag):
        return 'http://twitter.com/search?%s' %(urlencode({'q': hashtag}))
    
urls = AppUrls()

helpers['urls'] = urls