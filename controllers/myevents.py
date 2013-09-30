import web

from model import Poll

from . import pagerender as render
from . import edit

class myevents:

    def _get_poll(self, poll_url_code):
        poll = Poll.get_by_url(web.ctx.orm, poll_url_code)
        if poll is None:
            raise web.ctx.notfound()
        return poll

    def GET(self, poll_url=None):
        user = web.ctx.auth.current_user()
        if user is None:
            url = web.ctx.urls.sign_in(web.ctx.urls.polls_list())
            return web.seeother(url) # go sign in and then come back

        polls = user.polls_by_start()
        poll = None
        form = None
        if poll_url:
            # look up the poll based on the url
            poll = self._get_poll(poll_url)

            # make sure it belongs to the current user
            if poll.user != user:
                web.ctx.log.warn('Illegal poll access by user', user.id, poll.id)
                raise web.forbidden()

            form = edit.populate_form(poll)

        return render.myevents(user, polls, poll, form)
