import web

from . import elements

from model import Poll, Question, Response

class response:

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

        return poll

    def _auth_question(self, question_id, poll):
        question = web.ctx.orm.query(Question).get(question_id)
        if not question:
            raise web.notfound("No such question")

        elif question.poll_id != poll.id:
            raise web.badrequest("Question does not go with that event")

        return question


    def _process_response(self, poll):
        input = web.input()

        user = web.ctx.auth.current_user()

        questionId = input.get('question', None)
        if questionId is None:
            raise web.badrequest("Question id not provided")

        question = self._auth_question(questionId, poll)

        answer = input.get('answer', None)
        if answer is None:
            raise web.badrequest('Answer not provided')

        try:
            answer = int(answer)
        except ValueError:
            raise web.badrequest("Invalid answer")

        answerChoices = question.get_answer_choices()
        if answer < 0 or answer > len(answerChoices):
            raise web.badrequest('Not a valid answer to this question')
        web.ctx.log.warn("I am here! 3")
        # maybe they already answered it
        response = user.first_response(question)
        if response is None:
            response = Response()
            response.poll = poll
            response.question = question
            response.user = user
            web.ctx.orm.add(response)
        web.ctx.log.warn("I am here! 4")
        # save the response
        response.visit = None;
        response.answer = answer

        return question

    def POST(self, poll_url):

        poll = self._auth_poll(poll_url, require_login=True)

        question = self._process_response(poll)

        result = elements.question(question)
        raise web.created(data=result)

