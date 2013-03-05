import web

from . import pagerender as render

class poll:
    def GET(self, poll_url):
        # look up the poll based on the url
        poll = None
        
        # display the poll
        return render.poll(poll)
    
    def POST(self, poll_url):
        # look up the poll based on the url
        poll = None
        
        # save the response
        
        # go to the results page
        web.seeother('/results')