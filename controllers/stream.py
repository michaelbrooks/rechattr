import web
from datetime import datetime
from utils.dtutils import utc_aware, dt_timestamp

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

        # look up the poll based on the url
        poll = self._get_poll(poll_url)

        try:
            since = float(i.get('since', 0))
            since = utc_aware(datetime.utcfromtimestamp(since))
        except:
            raise web.badrequest('parameter "since" must be a timestamp')

        before = i.get('before', None)
        if before is not None:
            try:
                before = float(before)
                before = utc_aware(datetime.utcfromtimestamp(before))
            except:
                raise web.badrequest('parameter "before" must be a timestamp')

        items = poll.get_stream(newer_than=since, older_than=before)

        # render any stream items
        html = ''
        for item in items:
            html += str(render_stream_item(item, True))

        if len(items):
            time_to = dt_timestamp(items[0].get_time())
            time_from = dt_timestamp(items[-1].get_time())
        else:
            time_to = None
            time_from = None

        response = {
            'html': html,
            'items': len(items),
            'time_to': time_to,
            'time_from': time_from
        }
        
        # display the poll
        return web.ctx.json(response)