import web

from datetime import datetime
from dateutil.tz import tzoffset, tzutc
import time

from libs import Auth

import os

from . import pagerender as render

class sign_in:
        
    def GET(self):
        auth = Auth()
        i = web.input()
        
        # the ultimate destination, or home
        return_to = i.get('return_to', web.ctx.home)
        print 'foo'
        user = auth.current_user()
        print 'bar'
        if user is not None:
            # We were already signed in. ha!
            return web.seeother(return_to)
        
        if 'oauth_verifier' in i:
            auth.finish_auth(i)
            return web.seeother(return_to)
        elif 'denied' in i:
            auth.cancel_auth(i)
            return web.seeother(return_to)
        else:
            
            # This is a new sign in request
            # generate the url for users returning from Twitter auth
            return_url = web.ctx.home + web.http.url(return_to=return_to)
            
            # get the token and redirect from Twitter
            twitter_url = auth.get_redirect_url(return_url)
            
            # redirect
            return web.seeother(twitter_url)
        
    def POST(self):
        
        pass
