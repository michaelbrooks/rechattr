import web

from model import Poll

from . import pagerender as render

class index:
        
    def GET(self):
        user = web.ctx.auth.current_user()
        if user is None:
            url = web.ctx.urls.sign_in(web.ctx.urls.polls_list())
            web.seeother(url) # go sign in and then come back
            
        polls = web.ctx.orm.query(Poll).order_by(Poll.created).all()
        
        return render.index(user, polls)
