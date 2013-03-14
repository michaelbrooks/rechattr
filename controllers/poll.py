import web
import simplejson as json

from . import pagerender as render
from model import Poll, Response

class poll:
    def _get_poll(self, poll_url_code):
        poll = web.ctx.orm.query(Poll).filter(Poll.poll_url_code == poll_url_code).first();
        if poll is None:
            raise web.ctx.notfound()
        return poll

    def GET(self, poll_url):
        # look up the poll based on the url
        poll = self._get_poll(poll_url)
        
        # display the poll
        return render.poll(poll)
    
    def POST(self, poll_url):
        # look up the poll based on the url
        poll = self._get_poll(poll_url)
        
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