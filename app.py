import web
import db, model
import appconfig as conf

urls = (
    '/', 'index'
)

web.config.debug = conf.DEBUG

render = web.template.render('templates/')

app = web.application(urls, globals())
app.add_processor(db.load_sqla)

class index:
    def get_emails(self):
        emails = [e.user_email for e in web.ctx.orm.query(model.Poll.user_email)]
        return emails
        
    def GET(self):
        emails = self.get_emails()
        return render.index(emails)

    def POST(self):
        i = web.input()
        
        poll = model.Poll()
        poll.user_email = i.email
        web.ctx.orm.add(poll)
        
        emails = self.get_emails()
        return render.index(emails)
        
if __name__ == "__main__":
    app.run()
