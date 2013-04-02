import web
from model import Poll

from . import pagerender as render

class edit:
    def _get_poll(self, poll_url_code):
        poll = Poll.get_by_url(web.ctx.orm, poll_url_code)
        if poll is None:
            raise web.ctx.notfound()
        return poll
        
    def GET(self, poll_url):
        # look up the poll based on the url
        poll = self._get_poll(poll_url)
        
        user = web.ctx.auth.current_user()
        if user is None:
            url = web.ctx.urls.sign_in(web.ctx.urls.poll_edit(poll))
            return web.seeother(url) # go sign in and then come back
        
        # make sure it belongs to the current user
        if poll.user != user:
            web.ctx.log.warn('Illegal poll access by user', user.id, poll.id)
            raise web.ctx.notfound()
        
        # generate an edit form
        return render.edit(poll)
    
    def POST(self, poll_url, edit_url):
        # look up the poll and make sure the form is valid
        poll = self._get_poll(poll_url)
        
        # update the poll based on the input
        i = web.input()
        
        # generate an edit form
        return render.edit(poll)