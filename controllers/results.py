import web

from model import Poll

from . import pagerender as render

class results:
    def _get_poll(self, poll_url_code):
        poll = web.ctx.orm.query(Poll).filter(Poll.poll_url_code == poll_url_code).first();
        if poll is None:
            raise web.ctx.notfound()
        return poll
        
    def GET(self, poll_url):
        # look up the poll based on the url
        poll = self._get_poll(poll_url)
        
        return render.results(poll)