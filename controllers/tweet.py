import web

from . import elements

import utils
from model import Poll, Question, Tweet
from utils import twttr
from tweepy import TweepError

class tweet:
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

    def _auth_question(self, question_id, poll):
        question = web.ctx.orm.query(Question).get(question_id)
        if not question:
            raise web.notfound("No such question")

        elif question.poll_id != poll.id:
            raise web.badrequest("Question does not go with that event")

        return question

    def _record_tweet(self, poll, user, tweetText, question=None):

        api = web.ctx.auth.tweepy()
        status = api.update_status(tweetText);

        # go ahead and add it
        # we will link it to the current poll,
        # but potentially miss any concurrent overlapping polls
        # unsure whether the subsequent stream arrival will overwrite.
        tweet = Tweet(status)

        # TODO: link tweets to questions
        #tweet.question = question

        # TODO: remove middle relation between polls and tweets
        tweet.polls.append(poll)

        web.ctx.orm.add(tweet)

        # try:
        # web.ctx.orm.commit()
        # except:
        # web.ctx.orm.rollback()
        # raise

        return tweet

    def _process_tweet_input(self, poll, question=None):
        input = web.input()

        # Build a checker for the hashtag
        containsHashtag = twttr.hashtag_contains(poll.twitter_hashtag)

        invalidInput = False
        if 'tweet' not in input:
            raise web.badrequest("You didn't write a message")

        tweet_text = input.get('tweet')
        hashtagPresent = containsHashtag(tweet_text)

        # if form_submit we can't expect auto hashtag addition
        if not containsHashtag(tweet_text):
            # just add the hashtag
            tweet_text += ' ' + poll.twitter_hashtag

        if len(tweet_text) > twttr.TWITTER_LENGTH_LIMIT:
            raise web.badrequest('Message longer than %s letters.' %(twttr.TWITTER_LENGTH_LIMIT))

        question_id = input.get('question')
        question = None
        if question_id:
            question = self._auth_question(question_id, poll)

        message = "Unknown error"
        try:
            return self._record_tweet(poll, tweet_text, question)

        except TweepError, e:
            code, message = utils.parse_tweep_error(e)
            web.ctx.log.error('Tweepy error saving tweet', tweet, e)

        except Exception, e:
            web.ctx.log.error('Unknown error saving tweet', tweet, e)

        raise web.internalerror(message)

    def POST(self, poll_url):

        poll = self._auth_poll(poll_url, require_login=True)

        tweet = self._process_tweet_input(poll)

        if not tweet:
            raise web.internalerror("Sorry, tweet could not be sent.")

        result = elements.tweet(tweet, newItem=True)
        raise web.created(data=result)