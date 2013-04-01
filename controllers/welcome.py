import web

from . import pagerender as render

class welcome:
        
    def GET(self):
        user = web.ctx.auth.current_user()
        return render.welcome(user)
