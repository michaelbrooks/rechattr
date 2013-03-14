import web

from model import Poll

from . import pagerender as render

class index:
        
    def GET(self):
        polls = web.ctx.orm.query(Poll).all()
        return render.index(polls)
