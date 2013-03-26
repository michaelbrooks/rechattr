import web

from . import pagerender as render

class sign_in:
        
    def GET(self):
        i = web.input()
        
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
                    web.ctx.flash.info("Welcome, %s." %(user.full_name))
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
        except Exception, e:
            web.ctx.log.error('Sign in error', e)
            web.ctx.flash.error("Sorry, something went wrong signing in.")
            return web.seeother(return_to)
            
    def POST(self):
        
        pass
