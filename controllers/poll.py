import web
from web import form
import simplejson as json
from tweepy import TweepError

import utils
from utils import twttr

from . import pagerender as render
from model import Poll, Response, Tweet, Question

DEFAULT_STREAM_LIMIT = 20

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
        stream = poll.get_stream(limit=DEFAULT_STREAM_LIMIT)

        tweetForm = tweet_form()
        if user is not None:
            stats = user.poll_stats(web.ctx.orm, poll)
        else:
            stats = None
        # display the poll
        return render.poll(user=user, poll=poll,
                           stream=stream,
                           tweetForm=tweetForm, stats=stats)

    def _process_answer(self, poll):
        input = web.input();

        questionId = input.get('id', None)
        if questionId is None:
            raise web.badrequest("Question id not provided")

        question = web.ctx.orm.query(Question).get(questionId)
        if question is None:
            raise web.notfound('Question not found')

        # make sure it belongs to this poll
        if question.poll != poll:
            raise web.badrequest('Question for wrong poll')

        answer = input.get('answer', None)
        if answer is None:
            raise web.badrequest('Answer not provided')

        answerChoices = question.get_answer_choices()
        if answer not in answerChoices:
            raise web.badrequest('Not a valid answer to this question')

        # save the response
        response = Response()
        response.poll = poll
        response.question = question
        response.user = web.ctx.auth.current_user() # might be None
        response.visit = None;
        response.answer = answer

        web.ctx.orm.add(response)

        return 'Response recorded';

    def _process_tweet_input(self, poll):
        input = web.input()
        tweetForm = tweet_form()
        
        # Build a checker for the hashtag
        containsHashtag = twttr.hashtag_contains(poll.twitter_hashtag)
        
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
            elif len(tweet) > twttr.TWITTER_LENGTH_LIMIT:
                response = {
                    'message': 'Message over %s letters.' %(twttr.TWITTER_LENGTH_LIMIT),
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
                    code, message = utils.parse_tweep_error(e)
                    web.ctx.log.error('Tweepy error saving tweet', tweet, e)
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
                stream = poll.get_stream(limit=DEFAULT_STREAM_LIMIT)
                user = web.ctx.auth.current_user()
                
                if user is not None:
                    stats = user.poll_stats(web.ctx.orm, poll)
                else:
                    stats = None
                    
                return render.poll(user=user, poll=poll,
                                   stream=stream,
                                   tweetForm=tweetForm, stats=stats)
            else:
                # redirect to avoid double submit
                web.ctx.flash.set(response)
                return web.seeother(web.ctx.urls.poll(poll))
        else:
            # we only need to render a confirmation message
            return json.dumps(response)
    
    def POST(self, poll_url, type):
        # look up the poll based on the url
        poll = self._get_poll(poll_url)

        if type == 'tweet':
            return self._process_tweet_input(poll)
        elif type == 'answer':
            return self._process_answer(poll)
        else:
            raise web.badrequest("Unknown request type %s." %(type));