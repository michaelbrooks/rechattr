import web
from web import form

from . import pagerender as render

valid_email = form.regexp(r'.+@.+\..+', 
                          'Must be a valid email address')
valid_date = form.Validator('Must be a valid date', 
                            lambda ts : int(ts) >= 0)
valid_terms = form.regexp(r'^\s*[#@\w+]+(\s*,\s*[#@\w+]+)*\s*$',
                          'Must be a comma-separated list of terms')
                          
create_form = form.Form(
    form.Textbox('email', form.notnull, valid_email, 
                 description='Your email',
                 class_="input-large", placeholder="Email"),
    form.Textbox('start', form.notnull, valid_date, 
                 placeholder="Start",
                 description='Event start'),
    form.Textbox('stop', form.notnull, valid_date, 
                 placeholder="Stop",
                 description='Event stop'),
    form.Textbox('terms', form.notnull, valid_terms, 
                 description='Twitter terms'),
    form.Button('submit', type='submit', 
                class_="btn btn-primary",
                description='Create')
)

class create:
    def GET(self):
        
        form = create_form()
        
        # use it to populate the form
        return render.create(form)
        
    def POST(self):
        # validate the form
        form = create_form()
        if not form.validates():
            return render.create(form)
        # create a new poll with the input
        poll = None
        i = web.input()
        
        # send a confirmation email
        
        # save the poll in the database
        
        # go to the results page
        web.seeother('/results')