import web
from web import form, net
from utils import dtutils, twttr
import simplejson as json
from datetime import datetime, timedelta

def nullable(validator):
    return form.Validator(validator.msg,
                          lambda v: validator.valid(v) if bool(v) else True)

# Make sure the hashtag is not in the restricted set of url segments
def legal_url_segment(ht):
    print valid_hashtag.test(ht)
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
valid_hashtag = form.Validator('Not a valid hashtag', twttr.valid_hashtag)
valid_terms = form.regexp(r'^\s*[#@\w+]+(\s*,\s*[#@\w+]+)*\s*$',
                          'Must be a comma-separated list of terms')
valid_timezone = form.Validator('Invalid timezone', dtutils.valid_timezone)
                          
class Datebox(form.Textbox):
    def __init__(self, name, description="", class_=''):
        class_ = 'input-mini date-box %s' % class_
        super(Datebox, self).__init__(
             name, form.notnull, valid_date, 
             placeholder="mm/dd/yyyy",
             autocomplete="off",
             description=description,
             class_=class_)
    
    def render(self):
        input = super(Datebox, self).render()
        return '<div class="date-picker">%s</div>' % input
        
class Timebox(form.Textbox):
    def __init__(self, name, description="", class_=""):
        class_ = 'input-mini time-box %s' % class_
        super(Timebox, self).__init__(
             name, form.notnull, valid_time,
             placeholder="hh:mm",
             autocomplete="off",
             description=description,
             class_=class_)
    
    def render(self):
        input = super(Timebox, self).render()
        return '<div class="time-picker">%s</div>' % input

class TZTimezone(form.Dropdown):
    def __init__(self, name, *validators, **attrs):
        self.show = None
        items = dtutils.human_timezones()
        super(TZTimezone, self).__init__(name, items, *validators, **attrs)

    def render(self):
        attrs = self.attrs.copy()
        attrs['name'] = self.name
        
        x = '<select %s>\n' % attrs
        
        allItems = []
        topItems = []
        for hName in self.args:
            tzCode = dtutils.tz_code(hName)
            zone = dtutils.tz(tzCode)
            
            now = datetime.now(zone)
            shortName = now.tzname()
            offset = now.utcoffset()
            
            # Generate a nice label
            label = dtutils.nice_tz_name(shortName, offset, hName)
            
            # Add the US timezones to a separate list because we are US centric :)
            if dtutils.tz_in_us(hName):
                topItems.append((tzCode, label, offset, shortName))
            else:
                allItems.append((tzCode, label, offset, shortName))
        
        offsetSort = lambda t: t[2]
        
        items = [('', 'Select a timezone', None, None)]
        
        # Sort both lists by offset from GMT
        allItems = sorted(allItems, key=offsetSort)
        items.extend(sorted(topItems, key=offsetSort))
        
        # add a divider and combine the lists
        items.append(('-', '---------------', None, None))
        items.extend(allItems)
        
        # Render the items
        for value, desc, offset, shortCode in items:
            x += self._render_option(value, desc, shortCode)
        
        x += '</select>\n'
        return x
    
    def validate(self, value):
        valid = super(TZTimezone, self).validate(value)
        if self.value:
            self.set_timezone_code(self.value)
        return valid
    
    def set_timezone_code(self, selected):
        try:
            zone = dtutils.tz(selected)            
            now = datetime.now(zone)
            self.value = selected
            self.show = now.tzname()
        except:
            self.value = None
            web.ctx.log.error('Invalid timezone code', selected)
            
    def _render_option(self, value, desc, shortCode, indent='  '):
        if self.value == value or (isinstance(self.value, list) and value in self.value):
            select_p = ' selected="selected"'
        else:
            select_p = ''
            
        if shortCode:
            select_p += ' data-code="%s"' %(shortCode)
            
        return indent + '<option%s value="%s">%s</option>\n' % (select_p, net.websafe(value), net.websafe(desc))