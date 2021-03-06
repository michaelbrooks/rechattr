import web
import tweepy
from datetime import datetime
from utils.dtutils import utc_aware
from model import User

class Auth(object):

    def __init__(self, oauth_key, oauth_secret):
        self._oauth = tweepy.OAuthHandler(oauth_key, oauth_secret)
        self._user = None
    
    def get_redirect_url(self, return_url):
    
        # Get a request token from Twitter
        auth = self._oauth
        auth.callback = return_url
        redirect_url = auth.get_authorization_url(signin_with_twitter=True)
            
        web.ctx.session['twitter_request_token'] = (auth.request_token.key,
                                                    auth.request_token.secret)
        
        return redirect_url
        
    def tweepy(self, auth=None):
        if auth is None:
            auth = self._oauth
        return tweepy.API(auth)
        
    def finish_auth(self, input):
        verifier = input.get('oauth_verifier')
        
        request_key, request_secret = web.ctx.session['twitter_request_token']
        
        auth = self._oauth
        auth.set_request_token(request_key, request_secret)
        auth.get_access_token(verifier)
        
        # make a tweepy api instance
        api = self.tweepy(auth)
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
        self._user.last_signed_in = utc_aware()
        
        try:
            web.ctx.orm.commit()
        except:
            web.ctx.orm.rollback()
            raise
        
        self.reset_session()
        
        # sign them in
        web.ctx.session['user_id'] = self._user.id
        web.ctx.session['oauth_key'] = auth.access_token.key
        web.ctx.session['oauth_secret'] = auth.access_token.secret

        # don't need this any more
        del web.ctx.session['twitter_request_token']
        
        return self._user
        
    def current_user(self):
        # Check for a signed in user
        if self._user is None and 'user_id' in web.ctx.session:
            user_id = web.ctx.session.get('user_id', None)
            key = web.ctx.session.get('oauth_key', None)
            secret = web.ctx.session.get('oauth_secret', None)

            if not user_id or not key or not secret:
                return None

            self._user = web.ctx.orm.query(User).get(user_id)
            if self._user.oauth_key != key:
                web.ctx.log.warn('Session key does not match user key')
                self._user = None
                return None

            # configure the access token for auth
            self._oauth.set_access_token(key, secret)
        
        return self._user
        
    def sign_out(self):
        self._user = None
        del web.ctx.session['user_id']
        self.reset_session()
        
    def reset_session(self):
        # delete the old session from the db
        del web.ctx.session.store[web.ctx.session.session_id]
        # generate a new id - this will be saved automatically
        web.ctx.session.session_id = web.ctx.session._generate_session_id()