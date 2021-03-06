import web

import utils
from tweepy import TweepError
from . import pagerender as render

class sign_in:
    
    def _sign_out(self):
        web.ctx.auth.sign_out()
        return web.seeother(web.ctx.urls.home())
    
    def GET(self):
        i = web.input()
        
        path = web.ctx.path
        if path == '/sign_out':
            return self._sign_out()
            
        # the ultimate destination, or home
        return_to = i.get('return_to', web.ctx.home)
        
        # check if signed in
        user = web.ctx.auth.current_user()
        if user is not None:
            # We were already signed in. ha!
            return web.seeother(return_to)
        
        try:
            if 'oauth_verifier' in i:
                web.ctx.auth.finish_auth(i)
                
                user = web.ctx.auth.current_user()
                if user is None:
                    web.ctx.flash.error("Sorry, there was a problem signing in.")
                    web.ctx.log.error('No user after finish auth', e)
                else:
                    web.ctx.log.info('Sign in success', user.id)
                    
                return web.seeother(return_to)
            elif 'denied' in i:
                
                web.ctx.flash.warn("Sign in did not complete.")
                web.ctx.log.warn('twitter auth returned denied')
                return web.seeother(return_to)
            else:
                
                # This is a new sign in request
                # generate the url for users returning from Twitter auth
                return_url = web.ctx.home + web.http.url(return_to=return_to)
                
                # get the token and redirect from Twitter
                twitter_url = web.ctx.auth.get_redirect_url(return_url)
                    
                # redirect
                return web.seeother(twitter_url)
        except TweepError, e:
            code, message = utils.parse_tweep_error(e)
            web.ctx.log.error('Tweepy error signing in', e)
            if code == 130:
                message = "Sorry, Twitter not responding. Please try again in a moment."
            else:
                message = "Sorry, Twitter sign in failed. Please try again in a moment."
            web.ctx.flash.error(message)
            return web.seeother(return_to)
        except Exception, e:
            web.ctx.log.error('Sign in error', e)
            web.ctx.flash.error("Sorry, something went wrong signing in.")
            return web.seeother(return_to)
            
    def POST(self):
        
        pass
