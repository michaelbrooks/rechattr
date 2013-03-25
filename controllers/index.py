import web

from model import Poll
from libs import Auth

from . import pagerender as render

class index:
        
    def GET(self):
        polls = web.ctx.orm.query(Poll).order_by(Poll.created).all()
        auth = Auth()
        user = auth.current_user()
        return render.index(polls, user)
