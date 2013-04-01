import web
from web import form
import simplejson as json
import re
from tweepy import TweepError
from . import pagerender as render
from model import Poll, Response, Tweet

TWITTER_LENGTH_LIMIT = 140

##
# From https://github.com/twitter/twitter-text-java/blob/master/src/com/twitter/Regex.java
##
LATIN_ACCENTS_CHARS = "\\u00c0-\\u00d6\\u00d8-\\u00f6\\u00f8-\\u00ff" + \
                      "\\u0100-\\u024f" + \
                      "\\u0253\\u0254\\u0256\\u0257\\u0259\\u025b\\u0263\\u0268\\u026f\\u0272\\u0289\\u028b" + \
                      "\\u02bb" + \
                      "\\u0300-\\u036f" + \
                      "\\u1e00-\\u1eff";
HASHTAG_ALPHA_CHARS = "a-z" + LATIN_ACCENTS_CHARS + \
                        "\\u0400-\\u04ff\\u0500-\\u0527" + \
                        "\\u2de0-\\u2dff\\ua640-\\ua69f" + \
                        "\\u0591-\\u05bf\\u05c1-\\u05c2\\u05c4-\\u05c5\\u05c7" + \
                        "\\u05d0-\\u05ea\\u05f0-\\u05f4" + \
                        "\\ufb1d-\\ufb28\\ufb2a-\\ufb36\\ufb38-\\ufb3c\\ufb3e\\ufb40-\\ufb41" + \
                        "\\ufb43-\\ufb44\\ufb46-\\ufb4f" + \
                        "\\u0610-\\u061a\\u0620-\\u065f\\u066e-\\u06d3\\u06d5-\\u06dc" + \
                        "\\u06de-\\u06e8\\u06ea-\\u06ef\\u06fa-\\u06fc\\u06ff" + \
                        "\\u0750-\\u077f\\u08a0\\u08a2-\\u08ac\\u08e4-\\u08fe" + \
                        "\\ufb50-\\ufbb1\\ufbd3-\\ufd3d\\ufd50-\\ufd8f\\ufd92-\\ufdc7\\ufdf0-\\ufdfb" + \
                        "\\ufe70-\\ufe74\\ufe76-\\ufefc" + \
                        "\\u200c" + \
                        "\\u0e01-\\u0e3a\\u0e40-\\u0e4e" + \
                        "\\u1100-\\u11ff\\u3130-\\u3185\\uA960-\\uA97F\\uAC00-\\uD7AF\\uD7B0-\\uD7FF" + \
                        "\\p{InHiragana}\\p{InKatakana}" + \
                        "\\p{InCJKUnifiedIdeographs}" + \
                        "\\u3003\\u3005\\u303b" + \
                        "\\uff21-\\uff3a\\uff41-\\uff5a" + \
                        "\\uff66-\\uff9f" + \
                        "\\uffa1-\\uffdc";
HASHTAG_ALPHA_NUMERIC_CHARS = "0-9\\uff10-\\uff19_" + HASHTAG_ALPHA_CHARS;
HASHTAG_ALPHA = "[" + HASHTAG_ALPHA_CHARS +"]";
HASHTAG_ALPHA_NUMERIC = "[" + HASHTAG_ALPHA_NUMERIC_CHARS +"]";

VALID_HASHTAG = re.compile("(^|[^&" + HASHTAG_ALPHA_NUMERIC_CHARS + \
                           "])(#|\uFF03)(" + HASHTAG_ALPHA_NUMERIC + "*" + \
                           HASHTAG_ALPHA + HASHTAG_ALPHA_NUMERIC + "*)", \
                           re.IGNORECASE);
VALID_HASHTAG_GROUP_BEFORE = 1;
VALID_HASHTAG_GROUP_HASH = 2;
VALID_HASHTAG_GROUP_TAG = 3;
INVALID_HASHTAG_MATCH_END = re.compile("^(?:[##]|://)");

def hashtag_contains(hashtag):
    htmatch = VALID_HASHTAG.match(hashtag);
    if htmatch is None:
        raise Exception("Invalid hashtag")
        
    hashtag = htmatch.group(VALID_HASHTAG_GROUP_TAG)
    
    hashtagRegex = re.compile("(^|[^0-9A-Z&/]+)(#|\uFF03)(" + \
                              hashtag + \
                              ")($|[^#\uFF03" + HASHTAG_ALPHA_NUMERIC_CHARS + "])", \
                              re.IGNORECASE);
                              
    return lambda inputStr : hashtagRegex.search(inputStr)
    

tweet_form = form.Form(
    form.Textarea('tweet', form.notnull, 
                 class_="tweet-input"),
    form.Hidden('form_submit', type="hidden"),
    form.Button('submit', type='submit', 
                class_="btn btn-primary tweet-submit",
                disabled="disabled",
                html='Send Tweet')
)

class poll:
    def _get_poll(self, poll_url_code):
        poll = Poll.get_by_url(web.ctx.orm, poll_url_code)
        if poll is None:
            raise web.ctx.notfound()
        return poll
        
    def _record_tweet(self, poll, tweetText):
        user = web.ctx.auth.current_user()
        if user is None:
            return False
        
        api = web.ctx.auth.tweepy()
        status = api.update_status(tweetText);
        
        # go ahead and add it
        # we will link it to the current poll,
        # but potentially miss any concurrent overlapping polls
        # unsure whether the subsequent stream arrival will overwrite.
        tweet = Tweet(status)
        tweet.polls.append(poll)
        
        web.ctx.orm.add(tweet)
        # try:
            # web.ctx.orm.commit()
        # except:
            # web.ctx.orm.rollback()
            # raise
        
        return tweet
        
    
    def GET(self, poll_url):
        # look up the poll based on the url
        poll = self._get_poll(poll_url)
        user = web.ctx.auth.current_user()
        items = poll.tweet_stream(web.ctx.orm)
        tweetForm = tweet_form()
        if user is not None:
            stats = user.poll_stats(web.ctx.orm, poll)
        else:
            stats = None
        # display the poll
        return render.poll(user=user, poll=poll, items=items, tweetForm=tweetForm, stats=stats)
    
    def _process_tweet_input(self, poll, input):
        tweetForm = tweet_form()
        
        # Build a checker for the hashtag
        containsHashtag = hashtag_contains(poll.twitter_hashtag)
        
        invalidInput = False
        if not tweetForm.validates():
            response = {
                'message': "You didn't write a message!",
                'type': "error"
            }
            invalidInput = True
        else:
            tweet = input.get('tweet')
            hashtagPresent = containsHashtag(tweet)
            
            # if form_submit we can't expect auto hashtag addition
            if not hashtagPresent and 'form_submit' in input:                
                # just add the hashtag
                tweet += ' ' + poll.twitter_hashtag
                hashtagPresent = True
            
            # now if it isn't present we're screwed
            if not hashtagPresent:
                response = {
                    'message': "Must include %s." %(poll.twitter_hashtag),
                    'type': "error"
                }
                invalidInput = True
            elif len(tweet) > TWITTER_LENGTH_LIMIT:
                response = {
                    'message': 'Message over %s letters.' %(TWITTER_LENGTH_LIMIT),
                    'type': 'error'
                }
                invalidInput = True
            else:
                result = None
                try:
                    if self._record_tweet(poll, tweet):
                        response = {
                            'message': "Tweet posted!",
                            'type': "success"
                        }
                    else:
                        response = {
                            'message': "Sorry, tweet not sent.",
                            'type': "error"
                        }
                except TweepError, e:
                    web.ctx.log.error('Tweepy error saving tweet', tweet, e)
                    error = e.args[0][0] # the first error from the first argument
                    message = error['message']
                    code = error['code']
                    response = {
                        'message': message,
                        'type': "success"
                    }
                    invalidInput= True
                except Exception, e:
                    web.ctx.log.error('Unknown error saving tweet', tweet, e)
                
        if 'form_submit' in input:
            if invalidInput:
                # we have to re-render the whole page
                web.ctx.flash.set(response)
                items = poll.tweet_stream(web.ctx.orm)
                user = web.ctx.auth.current_user()
                
                if user is not None:
                    stats = user.poll_stats(web.ctx.orm, poll)
                else:
                    stats = None
                    
                return render.poll(user=user, poll=poll, items=items, tweetForm=tweetForm, stats=stats)
            else:
                # redirect to avoid double submit
                web.ctx.flash.set(response)
                return web.seeother(poll.poll_url())
        else:
            # we only need to render a confirmation message
            return json.dumps(response)
    
    def POST(self, poll_url):
        # look up the poll based on the url
        poll = self._get_poll(poll_url)
            
        i = web.input()
        if 'tweet' in i:
            return self._process_tweet_input(poll, i)
        else:
            answers = web.input()
            
            # save the response
            response = Response()
            response.poll = poll;
            response.visit = None;
            response.comment = None;
            response.answers = json.dumps(answers);
            web.ctx.orm.add(response)
        
            # go to the results page
            web.seeother(poll.results_url())