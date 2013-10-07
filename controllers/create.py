import web
from web import form

import simplejson as json
import re

from datetime import datetime
import time

from model import Poll
import hashlib
import os

from utils import csrf_protected, inputs, dtutils
from . import pagerender as render

sha1 = hashlib.sha1

create_form = form.Form(
    form.Textbox('email', inputs.nullable(inputs.valid_email),
                 class_="input-large", placeholder="My email address"),
    form.Textbox('title', form.notnull,
                 class_='input-large', placeholder="My Awesome Event"),
    inputs.Datebox('start_date', 'Event Start', 'start-date'),
    inputs.Timebox('start_time', '', 'start-time'),
    inputs.Datebox('stop_date', 'Event Stop', 'stop-date'),
    inputs.Timebox('stop_time', '', 'stop-time'),
    form.Textbox('twitter_hashtag', form.notnull, inputs.valid_hashtag, inputs.legal_url_validator,
                 placeholder="MyHashtag"),
    inputs.TZTimezone('tz_timezone', form.notnull, inputs.valid_timezone),
    form.Checkbox('tz_timezone_save', value="yes"),
    form.Button('submit', type='submit', 
                class_="btn btn-primary btn-large",
                html="Create my event")
)

class create:
    def _random_code(self, length):
        rand = os.urandom(16)
        now = time.time()
        code = sha1("%s%s%s" %(rand, now, web.utils.safestr(web.ctx.ip)))
        code = code.hexdigest()
        return code[:length].lower()

    def _create_poll_url(self, poll):
        #remove the #
        hashtag = poll.twitter_hashtag[1:]
        
        # the url starts with the hashtag only
        prefix = "%s" %(hashtag)
        
        # remove all non alphanumeric and lowercase it
        prefix = re.sub(r'[^\w]','-', prefix)
        
        append = 0
        code = prefix
        
        # check for uniqueness, increment append counter on failures
        match = Poll.get_by_url(web.ctx.orm, code)
        while match is not None:
            append += 1
            code = "%s-%s" %(prefix, append)
            match = Poll.get_by_url(web.ctx.orm, code)
            
        return code
        
    def GET(self):
        user = web.ctx.auth.current_user()
        if user is None:
            url = web.ctx.urls.sign_in(web.ctx.urls.new_poll())
            return web.seeother(url) # go sign in and then come back
        
        form = create_form()
        
        # make sure the timezone default is set
        if user.olson_timezone:
            form.tz_timezone.set_timezone_code(user.olson_timezone)
            
        # use it to populate the form
        return render.create(user, form)
        
    @csrf_protected
    def POST(self):
        user = web.ctx.auth.current_user()
        if user is None:
            url = web.ctx.urls.sign_in(web.ctx.urls.new_poll())
            web.ctx.flash.info("You must be signed in to create a poll")
            return web.seeother(url) # go sign in and then come back
        
        # validate the form
        form = create_form()
        if not form.validates():
            web.ctx.flash.error("Please check the form for problems.")
            return render.create(user, form)
        
        # create a new poll with the input
        poll = Poll()
        i = web.input()
        
        # save the title
        poll.title = i.title
        
        # parse the provided date and time given the provided tz info
        poll.olson_timezone = i.tz_timezone
        poll.event_start = dtutils.user_to_datetime(i.start_date, i.start_time, i.tz_timezone)
        poll.event_stop = dtutils.user_to_datetime(i.stop_date, i.stop_time, i.tz_timezone)
        
        # if they set to override the default, go ahead and set it on the user
        if i.get('tz_timezone_save', None) and user.olson_timezone != i.tz_timezone:
            user.olson_timezone = i.tz_timezone
        
        # if they provided an email then save it
        if i.email is not None and len(i.email) > 0:
            poll.email = i.email
        
        # save the hashtag
        poll.twitter_hashtag = Poll.clean_term(i.twitter_hashtag, '#')
        # poll.twitter_other_terms = i.twitter_other_terms
        
        # initialize the urls
        poll.poll_url_human = self._create_poll_url(poll)
        poll.poll_url_code = poll.poll_url_human.lower()
        poll.results_url_code = self._random_code(Poll.RESULTS_URL_CODE_LENGTH)
        poll.edit_url_code = self._random_code(Poll.EDIT_URL_CODE_LENGTH)
        #poll.short_url = ???
        
        # TODO: send a confirmation email
        
        # tie it to the current user
        poll.user = user
        
        # save the poll in the database
        web.ctx.orm.add(poll)
        
        # go to the edit page
        web.seeother(web.ctx.urls.poll_edit(poll))
        