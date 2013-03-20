import web
from model import Poll

from . import pagerender as render

class edit:
    def _get_poll(self, poll_url_code):
        poll = Poll.get_by_url(web.ctx.orm, poll_url_code)
        if poll is None:
            raise web.ctx.notfound()
        return poll
        
    def GET(self, poll_url, edit_url):
        # look up the poll based on the url
        poll = self._get_poll(poll_url)
        
        # generate an edit form
        return render.edit(poll)
    
    def POST(self, poll_url, edit_url):
        # look up the poll and make sure the form is valid
        poll = self._get_poll(poll_url)
        
        # update the poll based on the input
        i = web.input()
        
        # generate an edit form
        return render.edit(poll)