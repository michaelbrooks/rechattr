import web
from model import Poll

from . import pagerender as render

class index:
    def get_emails(self):
        emails = [e.user_email for e in web.ctx.orm.query(Poll.user_email)]
        return emails
        
    def GET(self):
        emails = self.get_emails()
        return render.index(emails)

    def POST(self):
        i = web.input()
        
        poll = Poll()
        poll.user_email = i.email
        web.ctx.orm.add(poll)
        
        emails = self.get_emails()
        return render.index(emails)