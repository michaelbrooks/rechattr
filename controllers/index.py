import web

from model import Poll

from . import pagerender as render

class index:
        
    def GET(self):
        polls = web.ctx.orm.query(Poll).order_by(Poll.created).all()
        user = web.ctx.auth.current_user()
        return render.index(polls, user)
