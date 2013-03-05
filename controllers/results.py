import web

from . import pagerender as render

class results:
    def GET(self, poll_url):
        # look up the poll based on the url
        poll = None
        
        return render.results(poll)