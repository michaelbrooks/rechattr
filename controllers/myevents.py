import web

from model import Poll

from . import pagerender as render

class myevents:

    def _get_poll(self, poll_url_code):
        poll = Poll.get_by_url(web.ctx.orm, poll_url_code)
        if poll is None:
            raise web.ctx.notfound()
        return poll

    def GET(self):
        user = web.ctx.auth.current_user()
        if user is None:
            url = web.ctx.urls.sign_in(web.ctx.urls.polls_list())
            return web.seeother(url) # go sign in and then come back

        polls = user.polls_by_start()

        return render.myevents(user, polls)
