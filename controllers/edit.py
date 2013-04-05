import web
import simplejson as json

from web import form
from model import Poll

from utils import inputs, dtutils
from . import pagerender as render

edit_form = form.Form(
    form.Textbox('email', inputs.nullable(inputs.valid_email),
                 class_="editable", placeholder="Email"),
    form.Textbox('title', form.notnull,
                 class_='editable', autocomplete="off",
                 placeholder="My Awesome Event"),
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
                 class_='editable')
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
        
        
    def _ajax_message(self, type, message, about):
        web.header('Content-Type', 'application/json')
        return json.dumps({
            'type': type,
            'message': message,
            'about': about
        });
    
    def _post_question(self, user, poll, input):
        # validate the input
        if 'subject' not in input or len(input.subject.strip()) == 0:
            return self._ajax_message('error', 'Required', 'subject')
        
        print input
        
        return self._ajax_message('wheee', 'asdf', None)
        
        
    def _post_poll(self, user, poll, input):
        pass
    
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
        
        input = web.input()
        
        # Check if it is a poll update or a question update
        if 'subject' in input:
            return self._post_question(user, poll, input)
        elif 'title' in input:
            return self._post_poll(user, poll, input)