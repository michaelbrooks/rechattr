import web
from web import form
from model import Poll

from utils import inputs, dtutils
from . import pagerender as render

edit_form = form.Form(
    form.Textbox('email', inputs.nullable(inputs.valid_email),
                 description='Your email',
                 class_="editable", placeholder="Email"),
    form.Textbox('title', form.notnull,
                 description='Event Name',
                 class_='editable', placeholder="My Awesome Event"),
    form.Textbox('start_time', form.notnull, inputs.valid_time,
                 class_="start-time",
                 placeholder="hh:mm",
                 autocomplete="off"),
    form.Textbox('stop_time', form.notnull, inputs.valid_time,
                 class_="stop-time",
                 placeholder="hh:mm",
                 autocomplete="off"),
    form.Textbox('start_date', form.notnull, inputs.valid_date, 
                 class_="start-date",
                 placeholder="mm/dd/yyyy",
                 autocomplete="off"),
    form.Textbox('stop_date', form.notnull, inputs.valid_date, 
                 class_="stop-date",
                 placeholder="mm/dd/yyyy",
                 autocomplete="off"),
    form.Textbox('twitter_hashtag', form.notnull, inputs.valid_hashtag, inputs.legal_url_validator,
                 class_='editable'),
    inputs.TZTimezone('tz_timezone', form.notnull, inputs.valid_timezone),
    form.Checkbox('tz_timezone_save', value="yes"),
    form.Hidden('gmt_offset', type='hidden'),
    form.Button('submit', type='submit', 
                class_="btn btn-primary",
                description='Save',
                html="Save Changes")
)

class edit:
    def _get_poll(self, poll_url_code):
        poll = Poll.get_by_url(web.ctx.orm, poll_url_code)
        if poll is None:
            raise web.ctx.notfound()
        return poll

    def _populate_form(self, form, poll):
        form.title.value = poll.title
        form.email.value = poll.email
        # slice off the hash
        form.twitter_hashtag.value = poll.twitter_hashtag[1:]
        
        user = web.ctx.auth.current_user()
        
        tzone = dtutils.tz(poll.olson_timezone)
        local_event_start = dtutils.local_time(poll.event_start, tzone)
        local_event_stop = dtutils.local_time(poll.event_stop, tzone)
        start_date, start_time = dtutils.datetime_to_user(local_event_start)
        stop_date, stop_time = dtutils.datetime_to_user(local_event_stop)
        
        form.start_date.value = start_date
        form.start_time.value = start_time
        form.stop_date.value = stop_date
        form.stop_time.value = stop_time
        
        # save/retrieve the timezone in the poll itself
        if poll.user.olson_timezone:
            form.tz_timezone.set_timezone_code(poll.user.olson_timezone)
        
        
    def GET(self, poll_url):
        # look up the poll based on the url
        poll = self._get_poll(poll_url)
        
        user = web.ctx.auth.current_user()
        if user is None:
            url = web.ctx.urls.sign_in(web.ctx.urls.poll_edit(poll))
            return web.seeother(url) # go sign in and then come back
        
        # make sure it belongs to the current user
        if poll.user != user:
            web.ctx.log.warn('Illegal poll access by user', user.id, poll.id)
            raise web.ctx.notfound()
        
        form = edit_form()
        self._populate_form(form, poll)
        
        # generate an edit form
        return render.edit(user, poll, form)
    
    def POST(self, poll_url):
        # look up the poll based on the url
        poll = self._get_poll(poll_url)
        
        user = web.ctx.auth.current_user()
        if user is None:
            url = web.ctx.urls.sign_in(web.ctx.urls.poll_edit(poll))
            return web.seeother(url) # go sign in and then come back
        
        # make sure it belongs to the current user
        if poll.user != user:
            web.ctx.log.warn('Illegal poll access by user', user.id, poll.id)
            raise web.ctx.notfound()
        
        # update the poll based on the input
        i = web.input()
        
        # generate an edit form
        return render.edit(user, poll)