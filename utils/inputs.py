from web import form

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

class Datebox(form.Textbox):
    def __init__(self, name, description="", class_=''):
        class_ = 'input-mini date-box %s' % class_
        super(form.Textbox, self).__init__(
             name, form.notnull, valid_date, 
             placeholder="mm/dd/yyyy",
             autocomplete="off",
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
             autocomplete="off",
             description=description,
             class_=class_)
    
    def render(self):
        input = super(form.Textbox, self).render()
        return '<div class="time-picker">%s</div>' % input