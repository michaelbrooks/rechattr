import web
from datetime import datetime
import time
from utils.dtutils import utc_aware

from model import Poll

from . import render_stream_item

class stream:
    def _get_poll(self, poll_url_code):
        poll = Poll.get_by_url(web.ctx.orm, poll_url_code)
        if poll is None:
            raise web.ctx.notfound()
        return poll

    def GET(self, poll_url):
        i = web.input()
        
        try:
            since = float(i.get('since', 0))
            since = utc_aware(datetime.utcfromtimestamp(since))
        except:
            raise web.badrequest('parameters "since" must be a timestamp')
        
        # look up the poll based on the url
        poll = self._get_poll(poll_url)
        
        items = poll.get_stream(newer_than=since)
        
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