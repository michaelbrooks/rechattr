import web

from web import form
from model import Poll, Question

from utils import inputs, dtutils
from . import pagerender as render

edit_form = form.Form(
    form.Textbox('email', inputs.nullable(inputs.valid_email),
                 class_="editable event-email", placeholder="Email",
                 title="Click to edit"),
    form.Textbox('title', form.notnull,
                 class_='editable event-title', autocomplete="off",
                 placeholder="My Awesome Event",
                 title="Click to edit"),
    inputs.Datebox('start_date', 'Event Start', 'start-date editable', "Click to edit"),
    inputs.Timebox('start_time', '', 'start-time  editable',"Click to edit"),
    inputs.Datebox('stop_date', 'Event Stop', 'stop-date  editable', "Click to edit"),
    inputs.Timebox('stop_time', '', 'stop-time  editable', "Click to edit"),
    inputs.TZTimezone('tz_timezone', form.notnull, inputs.valid_timezone),
    form.Checkbox('tz_timezone_save', value="yes"),
    form.Textbox('twitter_hashtag', form.notnull, inputs.valid_hashtag, inputs.legal_url_validator,
                 class_='editable event-hashtag',
                 title="Click to edit")
)

class edit:
    def _auth_poll(self, poll_url, require_login=False, require_own=False):

        if require_own:
            require_login=True

        # look up the poll based on the url
        poll = Poll.get_by_url(web.ctx.orm, poll_url)
        if poll is None:
            raise web.ctx.notfound()

        user = web.ctx.auth.current_user()
        if user is None and require_login:
            url = web.ctx.urls.sign_in(web.ctx.urls.poll_edit(poll))
            raise web.seeother(url) # go sign in and then come back

        # make sure it belongs to the current user
        if user and poll.user != user:
            if require_own:
                web.ctx.log.warn('Illegal poll access by user', user.id, poll.id)
                raise web.forbidden()
            user = None

        return poll

    def _post_poll(self, user, poll):
        input = web.input()

        # save the title
        poll.title = input.title

        # parse the provided date and time given the provided tz info
        poll.olson_timezone = input.tz_timezone
        poll.event_start = dtutils.user_to_datetime(input.start_date, input.start_time, input.tz_timezone)
        poll.event_stop = dtutils.user_to_datetime(input.stop_date, input.stop_time, input.tz_timezone)

        # if they set to override the default, go ahead and set it on the user
        if input.get('tz_timezone_save', None) and user.olson_timezone != input.tz_timezone:
            user.olson_timezone = input.tz_timezone

        # if they provided an email then save it
        if input.email is not None and len(input.email) > 0:
            poll.email = input.email

        # save the hashtag
        poll.twitter_hashtag = Poll.clean_term(input.twitter_hashtag, '#')

    @staticmethod
    def populate_form(poll):
        form = edit_form()
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

        form.tz_timezone.set_timezone_code(poll.olson_timezone)

        return form

    def GET(self, poll_url):
        # look up the poll based on the url
        poll = self._auth_poll(poll_url, require_own=True)
        user = web.ctx.auth.current_user()

        form = edit.populate_form(poll)
        
        # generate an edit form
        return render.edit(user, poll, form)
    
    def POST(self, poll_url):
        # look up the poll based on the url
        poll = self._auth_poll(poll_url, require_own=True)
        user = web.ctx.auth.current_user()

        # validate the form
        form = edit_form()
        if not form.validates():
            web.ctx.flash.error("Please check the form for problems.")
            return render.edit(user, poll, form)

        self._post_poll(user, poll)

        # on success, redirect to GET
        web.ctx.flash.success("Event information updated.")
        web.seeother(web.ctx.urls.poll_edit(poll))

