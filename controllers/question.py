import web

from model import Poll, Question
from utils import dtutils

from . import elements
from . import render_stream_item

class question:

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

    def _make_question(self, poll):
        question = Question()
        question.poll = poll

        question.question_text = "What do you think?"
        question.set_answer_choices([])

        # 5 minutes from start, or 5 minutes from now (whichever is greater)
        offset = dtutils.timedelta(seconds=5 * 60)
        now_offset = dtutils.utc_aware() + offset
        start_offset = poll.event_start + offset

        if now_offset > start_offset:
            offset = now_offset - poll.event_start

        question.update_trigger(False, offset.total_seconds())

        web.ctx.orm.add(question)
        web.ctx.orm.flush()

        return question

    def _update_question(self, question, input):
        if 'question_text' not in input or len(input.question_text) == 0:
            raise web.badrequest('Question text is required')

        import time
        time.sleep(1)

        if not input.trigger_seconds:
            raise web.badrequest('Offset in seconds is required')

        question.question_text = input.question_text
        answer_choices = []
        if 'answer_choices' in input:
            answer_choices = [s.strip() for s in input['answer_choices'].splitlines()]
        question.set_answer_choices(answer_choices)

        # Normalize the seconds trigger
        try:
            input.trigger_seconds = round(float(input.trigger_seconds))
        except:
            raise web.badrequest('Offset in seconds must be a number')

        question.update_trigger(False, input.trigger_seconds)

        web.ctx.orm.flush()

        return question

    def _delete_question(self, question):
        web.ctx.orm.delete(question)
        web.ctx.orm.flush()


    #Gets HTML for viewing a question
    def GET(self, poll_url, question_id):
        poll = self._auth_poll(poll_url)
        question = self._auth_question(question_id, poll)
        return render_stream_item(question)

    #Updates a question. Returns the question editor.
    def PUT(self, poll_url, question_id):
        poll = self._auth_poll(poll_url, require_own=True)

        question = self._auth_question(question_id, poll)

        input = web.input()
        if self._update_question(question, input):
            result = elements.question_editor(question)
            raise web.accepted(data=result)
        else:
            raise web.badrequest("Invalid question data")

    #Creates a new question. Returns the question editor.
    def POST(self, poll_url):
        poll = self._auth_poll(poll_url, require_own=True)

        question = self._make_question(poll)

        result = elements.question_editor(question)
        raise web.created(data=result)

    def DELETE(self, poll_url, question_id=None):
        poll = self._auth_poll(poll_url, require_own=True)

        if question_id is None:
            raise web.badrequest("No question given")

        question = self._auth_question(question_id, poll)

        self._delete_question(question)
