import web
from datetime import datetime
import time

from model import Poll, Tweet

from . import pagerender as render
from . import render_stream_item

class stream:
    def _get_poll(self, poll_url_code):
        poll = Poll.get_by_url(web.ctx.orm, poll_url_code)
        if poll is None:
            raise web.ctx.notfound()
        return poll
        
    def _stream_since(self, poll, since):
        query = web.ctx.orm.query(Tweet).\
                            filter(Tweet.created > since, Tweet.polls.contains(poll)).\
                            order_by(Tweet.created)
        return query.all()
        
    def GET(self, poll_url):
        i = web.input()
        
        try:
            since = float(i.get('since', 0))
            since = datetime.utcfromtimestamp(since)
        except:
            raise web.badrequest('parameters "since" must be a timestamp')
        
        # look up the poll based on the url
        poll = self._get_poll(poll_url)
        
        items = self._stream_since(poll, since)
        
        # render any stream items
        html = ''
        for item in items:
            html += str(render_stream_item(item, True))
        
        response = {
            'html': html,
            'items': len(items),
            'time': time.time()
        }
        
        # display the poll
        return web.ctx.json(response)