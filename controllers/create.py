import web
from web import form

import simplejson as json
import re

from datetime import datetime
from dateutil.tz import tzoffset, tzutc
import time

from model import Poll
import hashlib
import os

from utils import csrf_protected
from . import pagerender as render

def nullable(validator):
    return form.Validator(validator.msg,
                          lambda v: validator.valid(v) if bool(v) else True)

# Make sure the hashtag is not in the restricted set of url segments
def legal_url_segment(ht):
    if ht[0] == '#':
        ht = ht[1:]
    return ht.lower() not in ['events', 'new', 'sign_in', 'sign_out']
legal_url_validator = form.Validator('This word is reserved for re:chattr', legal_url_segment)

valid_email = form.regexp(r'.+@.+\..+', 
                          'Must be a valid email address')
valid_date = form.regexp(r'\d{1,2}/\d{1,2}/\d{2,4}',
                         'Must be a valid date')
valid_time = form.regexp(r'\d{1,2}:\d{2}(am|pm)?',
                         'Must be a valid time')
#optional atsign, any number of non-whitespace chars
valid_username = form.regexp(r'^\s*@?\S+\s*$',
                         'Not a valid username')
#optional hash, any number of non-whitespace chars
valid_hashtag = form.regexp(r'^\s*#?\S+\s*$',
                         'Not a valid hashtag')
valid_terms = form.regexp(r'^\s*[#@\w+]+(\s*,\s*[#@\w+]+)*\s*$',
                          'Must be a comma-separated list of terms')

sha1 = hashlib.sha1

class Datebox(form.Textbox):
    def __init__(self, name, description="", class_=''):
        class_ = 'input-mini date-box %s' % class_
        super(form.Textbox, self).__init__(
             name, form.notnull, valid_date, 
             placeholder="mm/dd/yyyy",
             description=description,
             class_=class_)
    
    def render(self):
        input = super(form.Textbox, self).render()
        return '<div class="date-picker">%s</div>' % input
        
class Timebox(form.Textbox):
    def __init__(self, name, description="", class_=""):
        class_ = 'input-mini time-box %s' % class_
        super(form.Textbox, self).__init__(
             name, form.notnull, valid_time, type="time",
             placeholder="hh:mm",
             description=description,
             class_=class_)
    
    def render(self):
        input = super(form.Textbox, self).render()
        return '<div class="time-picker">%s</div>' % input

create_form = form.Form(
    form.Textbox('email', nullable(valid_email),
                 description='Your email',
                 class_="input-large", placeholder="Email"),
    form.Textbox('title', form.notnull,
                 description='Event Name',
                 class_='input-large', placeholder="My Awesome Event"),
    Datebox('start_date', 'Event Start', 'start-date'),
    Timebox('start_time', '', 'start-time'),
    Datebox('stop_date', 'Event Stop', 'stop-date'),
    Timebox('stop_time', '', 'stop-time'),
    form.Textbox('twitter_hashtag', form.notnull, valid_hashtag, legal_url_validator,
                 description='Hashtag'),
    # form.Textbox('twitter_other_terms', 
                 # description='Other usernames / hashtags (Optional)'),
    form.Hidden('gmt_offset', type='hidden'),
    form.Button('submit', type='submit', 
                class_="btn btn-primary btn-large",
                description='Create',
                html="Create my event")
)

def clean_term(term, prefix):
    term = term.strip()
    if term.startswith(prefix):
        return term
    return "%s%s" %(prefix, term)

utc = tzutc()

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
        
        
    def _parse_date_time(self, date_str, time_str, gmt_offset_seconds):
        
        tzinfo = tzoffset(None, gmt_offset_seconds);
        
        date_time_str = "%s %s" %(date_str, time_str)
        
        parsed = datetime.strptime(date_time_str, "%m/%d/%Y %I:%M%p")
        
        parsed = parsed.replace(tzinfo=tzinfo)
        
        return parsed.astimezone(utc)
        
        
    def GET(self):
        user = web.ctx.auth.current_user()
        if user is None:
            url = web.ctx.urls.sign_in(web.ctx.urls.new_poll())
            return web.seeother(url) # go sign in and then come back
        
        form = create_form()
        
        # use it to populate the form
        return render.create(user, form)
        
    @csrf_protected
    def POST(self):
        user = web.ctx.auth.current_user()
        if user is None:
            url = web.ctx.urls.sign_in(web.ctx.urls.new_poll())
            web.ctx.flash.info("You must be signed in to create a poll")
            return web.seeother(url) # go sign in and then come back
    
        combo = nullable(valid_email)
        inp = web.input()
        test = lambda v: valid_email.valid(v) if bool(v) else True
        print test('asdf')
        print 'foo' if bool('test') else True
        print 'bar' if bool('') else True
        print inp.email
        print valid_email.valid(inp.email)
        
        print combo.valid(inp.email)
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
        
        # parse the provided date and time given the detected tz info
        gmt_offset_seconds = 60 * int(i.gmt_offset)
        poll.event_start = self._parse_date_time(i.start_date, i.start_time, gmt_offset_seconds)
        poll.event_stop = self._parse_date_time(i.stop_date, i.stop_time, gmt_offset_seconds)
         
        # if they provided an email then save it
        if i.email is not None and len(i.email) > 0:
            poll.email = i.email
        
        # save the hashtag
        poll.twitter_hashtag = clean_term(i.twitter_hashtag, '#')
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
        