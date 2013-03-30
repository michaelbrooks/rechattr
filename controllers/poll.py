import web
from web import form
import simplejson as json

from . import pagerender as render
from model import Poll, Response, Tweet

tweet_form = form.Form(
    form.Textarea('tweet', form.notnull,
                 class_="tweet-input"),
    form.Hidden('form_submit', type="hidden"),
    form.Button('submit', type='submit', 
                class_="btn btn-primary tweet-submit",
                description='Send')
)

class poll:
    def _get_poll(self, poll_url_code):
        poll = Poll.get_by_url(web.ctx.orm, poll_url_code)
        if poll is None:
            raise web.ctx.notfound()
        return poll
    
    def _poll_stream(self, poll):
        query = web.ctx.orm.query(Tweet).\
                            filter(Tweet.polls.contains(poll)).\
                            order_by(Tweet.created.desc())
        return query.all()
        
    def _record_tweet(self, poll, tweetText):
        user = web.ctx.auth.current_user()
        return False
        if user is None:
            return False
        
    
    def GET(self, poll_url):
        # look up the poll based on the url
        poll = self._get_poll(poll_url)
        items = self._poll_stream(poll)
        tweetForm = tweet_form()
        
        # display the poll
        return render.poll(poll, items, tweetForm)
    
    def POST(self, poll_url):
        # look up the poll based on the url
        poll = self._get_poll(poll_url)
        tweetForm = tweet_form()
        
        i = web.input()
        if 'tweet' in i:
            if tweetForm.validates():
                tweet = i.get('tweet')
                if self._record_tweet(poll, tweet):
                    response = {
                        'message': "Your message has been sent to Twitter.",
                        'type': "success"
                    }
                else:
                    response = {
                        'message': "Sorry, your tweet could not be sent.",
                        'type': "error"
                    }
                    
                if 'form_submit' in i:
                    # we have to re-render the whole page
                    # but redirect to avoid double submit
                    web.ctx.flash.set(response)
                    return web.seeother(poll.poll_url())
                else:
                    # we only need to render a confirmation message
                    return json.dumps(response)
            else:
                response = {
                    'message': "Invalid input",
                    'type': "error"
                }
                if 'form_submit' in i:
                    # we have to re-render the whole page
                    web.ctx.flash.set(response)
                    items = self._poll_stream(poll)
                    return render.poll(pool, items, tweetForm)
                else:
                    # we only need to render a message
                    return json.dumps(response)
        else:
            answers = web.input()
            
            # save the response
            response = Response()
            response.poll = poll;
            response.visit = None;
            response.comment = None;
            response.answers = json.dumps(answers);
            web.ctx.orm.add(response)
        
            # go to the results page
            web.seeother(poll.results_url())