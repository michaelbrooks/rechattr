from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String, Boolean, Float
from sqlalchemy.orm import relationship, backref
from datetime import datetime, timedelta
import simplejson as json
import time

# Get the shared base class for declarative ORM
from model import Base
from utils import dtutils
from utils.dtutils import utc_aware
from decorators import UTCDateTime


class Question(Base):
    __tablename__ = 'questions'

    # Record info
    id = Column(Integer, primary_key=True)
    created = Column(UTCDateTime, default=datetime.utcnow)

    #Poll info
    poll_id = Column(Integer, ForeignKey('polls.id'))
    poll = relationship('Poll',
                        backref=backref('questions', order_by=created))

    # Question info
    trigger_manual = Column(Boolean, default=False)
    trigger_seconds = Column(Float, default=None)
    image_src = Column(String)
    subject = Column(String)
    question_text = Column(String)
    answer_choices = Column(String)

    def get_answer_choices(self):
        if not hasattr(self, '_cached_answers'):
            self._cached_answers = json.loads(self.answer_choices)
        return self._cached_answers

    def set_answer_choices(self, answers):
        self.answer_choices = json.dumps(answers)
        self._cached_answers = answers

    def percent_through_event(self):
        """
        Get the percent through the event when this question
        is triggered. If there is no trigger time, this will return None.

        :return:
        """
        if self.trigger_seconds is None:
            return None
        duration = self.poll.duration().total_seconds()
        return self.trigger_seconds / duration;

    def nice_offset(self):
        if self.trigger_seconds is None or self.trigger_manual:
            return 'manual'

        delta = timedelta(seconds=self.trigger_seconds)
        return dtutils.full_delta(delta, long=True, smallest="minutes")

    def nice_time(self):
        if self.trigger_seconds is None or self.trigger_manual:
            return 'manual'

        delta = timedelta(seconds=self.trigger_seconds)
        trigger = self.poll.event_start + delta

        tzone = dtutils.tz(self.poll.olson_timezone)
        local_trigger = dtutils.local_time(trigger, tzone)

        return local_trigger.strftime("%I:%M%p").lstrip('0')

    def triggered(self):
        # see if manually triggered first
        if self.trigger_manual:
            return True

        # then see if time triggered
        if self.trigger_seconds is not None:
            seconds = self.trigger_seconds
            trigger_delta = timedelta(0, seconds)

            start = self.poll.event_start
            now = utc_aware()
            delta = now - start

            return delta > trigger_delta

        return False

    def get_time(self):
        if self.trigger_seconds is None:
            return None

        offset_delta = timedelta(seconds=self.trigger_seconds)
        return self.poll.event_start + offset_delta

    def set_trigger_now(self):
        """
        Set the trigger time to now.

        # Should not set decimal-valued times
        >>> q = Question()
        >>> from model import Poll
        >>> q.poll = Poll()
        >>> q.poll.event_start = utc_aware() - timedelta(seconds=500.245)
        >>> q.set_trigger_now()
        >>> q.trigger_seconds == round(q.trigger_seconds)
        True
        """
        # Record the time offset against the poll start, in seconds
        offset_delta = (utc_aware() - self.poll.event_start)
        self.trigger_seconds = round(offset_delta.total_seconds())

    def update_trigger(self, new_manual, new_seconds):
        """
        Update the state of the trigger.
        :param new_manual: True or False
        :param new_seconds: None or a float time offset in seconds

        # A helper function to initialize a Question with mocked triggered() method
        >>> def prep(triggered=False, now=23):
        ...     q = Question()
        ...     # set the defaults (State 1)
        ...     q.trigger_manual = False
        ...     q.trigger_seconds = None
        ...
        ...     q.triggered = lambda: triggered
        ...
        ...     def mocked_set():
        ...         q.trigger_seconds = now
        ...
        ...     q.set_trigger_now = mocked_set
        ...
        ...     return q

        # Transition from State 1 to 2
        >>> q = prep()
        >>> q.trigger_manual, q.trigger_seconds
        (False, None)
        >>> q.update_trigger(False, 4)
        >>> q.trigger_manual, q.trigger_seconds
        (False, 4)

        # Transition from State 1 to 3
        >>> q = prep(now=52)
        >>> q.trigger_manual, q.trigger_seconds
        (False, None)
        >>> q.update_trigger(True, 4)
        >>> q.trigger_manual, q.trigger_seconds
        (True, 52)

        # Transition from State 1 to 3 - no time given
        >>> q = prep(now=52)
        >>> q.trigger_manual, q.trigger_seconds
        (False, None)
        >>> q.update_trigger(True, None)
        >>> q.trigger_manual, q.trigger_seconds
        (True, 52)

        # Transition from State 2 to 1
        >>> q = prep()
        >>> q.trigger_manual = False
        >>> q.trigger_seconds = 6
        >>> q.update_trigger(False, None)
        >>> q.trigger_manual, q.trigger_seconds
        (False, None)

        # Transition from State 2 to 3 - not yet triggered
        >>> q = prep(now=65)
        >>> q.trigger_manual = False
        >>> q.trigger_seconds = 6
        >>> q.update_trigger(True, None)
        >>> q.trigger_manual, q.trigger_seconds
        (True, 65)

        # Transition from State 2 to 3 - already triggered
        >>> q = prep(now=65, triggered=True)
        >>> q.trigger_manual = False
        >>> q.trigger_seconds = 6
        >>> q.update_trigger(True, None)
        >>> q.trigger_manual, q.trigger_seconds
        (True, 6)

        # Transition from State 3 to 1
        >>> q = prep()
        >>> q.trigger_manual = True
        >>> q.trigger_seconds = 6
        >>> q.update_trigger(False, None)
        >>> q.trigger_manual, q.trigger_seconds
        (False, None)

        # Transition from State 3 to 2
        >>> q = prep()
        >>> q.trigger_manual = True
        >>> q.trigger_seconds = 6
        >>> q.update_trigger(False, 42)
        >>> q.trigger_manual, q.trigger_seconds
        (False, 42)

        # Update time in State 2
        >>> q = prep()
        >>> q.trigger_manual = False
        >>> q.trigger_seconds = 6
        >>> q.update_trigger(False, 43)
        >>> q.trigger_manual, q.trigger_seconds
        (False, 43)
        """

        # State 1: manual=False, seconds=None
        if not self.trigger_manual and self.trigger_seconds is None:

            if new_manual: # ignore seconds

                # transition to State 3
                self.trigger_manual = True
                self.set_trigger_now()

            elif (not new_manual) and (new_seconds is not None):

                # transition to State 2
                self.trigger_seconds = new_seconds

            else:
                # otherwise we stay put
                pass

        # State 2: manual=False, seconds=something
        elif not self.trigger_manual and self.trigger_seconds is not None:

            if (not new_manual) and (new_seconds is None):

                # transition to State 1
                self.trigger_seconds = None

            elif new_manual: # ignore seconds

                # transition to State 3
                # only set the time if not already triggered
                if not self.triggered():
                    self.set_trigger_now()
                self.trigger_manual = True

            else:
                # just update the time
                self.trigger_seconds = new_seconds

        # State 3: manual=True, seconds=something
        elif self.trigger_manual and self.trigger_seconds is not None:

            if (not new_manual) and (new_seconds is not None):
                # transition to State 2
                self.trigger_manual = False
                self.trigger_seconds = new_seconds

            elif (not new_manual) and (new_seconds is None):
                # transition to State 1
                self.trigger_manual = False
                self.trigger_seconds = None

            else:
                # otherwise we stay put
                pass

        else:
            raise Exception(
                "Question %s trigger state is invalid (%s, %s)" % (self.id, self.trigger_manual, self.trigger_seconds))