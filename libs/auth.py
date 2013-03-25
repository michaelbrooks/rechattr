import web
import tweepy
from datetime import datetime

from model import User
import appconfig as conf

class Auth(object):

    def __init__(self):
        self._oauth = None
        self._user = None
    
    def get_auth(self, return_url=None):
        if self._oauth is None:
            consumer_token = conf.TWITTER_STREAM_CONSUMER_KEY
            consumer_secret = conf.TWITTER_STREAM_CONSUMER_SECRET
            self._oauth = tweepy.OAuthHandler(consumer_token, consumer_secret, return_url)
            
        return self._oauth
    
    def get_redirect_url(self, return_url):
        # Get a request token from Twitter
        auth = self.get_auth(return_url)
        
        redirect_url = auth.get_authorization_url(signin_with_twitter=True)
            
        web.ctx.session['twitter_request_token'] = (auth.request_token.key,
                                                   auth.request_token.secret)
        
        return redirect_url
        
    def finish_auth(self, input):
        verifier = input.get('oauth_verifier')
        
        request_key, request_secret = web.ctx.session['twitter_request_token']
        
        auth = self.get_auth()
        auth.set_request_token(request_key, request_secret)
        auth.get_access_token(verifier)
        
        # make a tweepy api instance
        api = tweepy.API(auth)
        twitter_user = api.verify_credentials(skip_status=True, include_entities=False)
        
        # does this user already exist?
        self._user = web.ctx.orm.query(User).\
                                 filter(User.oauth_user_id == twitter_user.id).\
                                 first()
        
        # if not, make a new one
        if self._user is None:
            self._user = User(twitter_user.id, oauth_provider='Twitter')
            web.ctx.orm.add(self._user)
            
        # update with any changes from Twitter
        self._user.update(twitter_user, auth.access_token)
        self._user.last_signed_in = datetime.utcnow()
        web.ctx.orm.commit()
        
        # sign them in
        web.ctx.session['user_id'] = self._user.id
        
        # don't need this any more
        del web.ctx.session['twitter_request_token']
        
        return self._user
        
    def cancel_auth(self, input):
        denied_key = input['denied']
        request_key, request_secret = web.ctx.session['twitter_request_token']
        if denied_key == request_key:
            del web.ctx.session['twitter_request_token']
        else:
            raise 'Denied wrong key'
    
    def current_user(self):
        if (self._user is None) and ('user_id' in web.ctx.session):
            user_id = web.ctx.session['user_id']
            self._user = web.ctx.orm.query(User).get(user_id)
        
        return self._user
        