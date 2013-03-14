import web

from model import Base

from . import pagerender as render

class clear_db:
        
    def GET(self):
        message = ""
        return render.clear_db(message)

    def POST(self):
        for tbl in reversed(Base.metadata.sorted_tables):
            web.ctx.orm.execute(tbl.delete())
            
        message = "Data deleted!"
        return render.clear_db(message)