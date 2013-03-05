import web

from . import pagerender as render

class edit:
    def GET(self, poll_url, edit_url):
        # look up the poll based on the url
        poll = None
        
        # generate an edit form
        return render.edit(poll)
    
    def POST(self, poll_url, edit_url):
        # look up the poll and make sure the form is valid
        poll = None
        
        # update the poll based on the input
        i = web.input()
        
        # generate an edit form
        return render.edit(poll)