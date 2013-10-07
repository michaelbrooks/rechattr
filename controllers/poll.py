import web

from . import pagerender as render
from model import Poll, Response, Tweet, Question

DEFAULT_STREAM_LIMIT = 20

class poll:
    def _get_poll(self, poll_url_code):
        poll = Poll.get_by_url(web.ctx.orm, poll_url_code)
        if poll is None:
            raise web.ctx.notfound()
        return poll
        
    def GET(self, poll_url):
        # look up the poll based on the url
        poll = self._get_poll(poll_url)
        user = web.ctx.auth.current_user()

        stream = poll.get_stream(limit=DEFAULT_STREAM_LIMIT)

        if len(stream):
            oldest_item = stream[-1]
            newest_item = stream[0]
        else:
            newest_item = None
            oldest_item = None

        lastQuestion = poll.triggered_questions(limit=1)
        if len(lastQuestion) and (not user or not user.first_response(lastQuestion[0])):
            lastQuestion = lastQuestion[0]
            if lastQuestion in stream:
                stream.remove(lastQuestion)
        else:
            lastQuestion = None

        if user is not None:
            stats = user.poll_stats(web.ctx.orm, poll)
        else:
            stats = None

        questionResponses = poll.get_question_responses()

        # display the poll
        return render.poll(user=user, poll=poll,
                           stream=stream, lastQuestion=lastQuestion,
                           newest_item=newest_item, oldest_item=oldest_item,
                           responses=questionResponses,
                           stats=stats)
