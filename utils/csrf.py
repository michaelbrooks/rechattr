import web
from uuid import uuid4
from utils.dtutils import utc_aware

def csrf_token():
    if not web.ctx.session.has_key('csrf_token'):
        web.ctx.session.csrf_token=uuid4().hex
    return web.ctx.session.csrf_token

def csrf_token_input():
    return '<input type="hidden" name="csrf_token" value="%s"/>' %(csrf_token())
    
def csrf_protected(f):
    def decorated(*args,**kwargs):
        inp = web.input()
        if not (inp.has_key('csrf_token') and inp.csrf_token == web.ctx.session.pop('csrf_token', None)):
            web.ctx.flash.warn("For your protection, the session was reset.")
            web.ctx.log.warn('CSRF failure', web.ctx.urls.requested())
            return web.seeother(web.ctx.urls.requested())
        return f(*args,**kwargs)
    return decorated
