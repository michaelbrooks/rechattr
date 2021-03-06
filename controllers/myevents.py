import web

from model import Poll

from . import pagerender as render

class myevents:
        
    def GET(self):
        user = web.ctx.auth.current_user()
        if user is None:
            url = web.ctx.urls.sign_in(web.ctx.urls.polls_list())
            return web.seeother(url) # go sign in and then come back

        polls = user.polls_by_start()
        
        return render.myevents(user, polls)
