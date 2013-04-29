define(function (require) {

    var $ = require('jquery');
    var url = require('util/url');
    var flash = require('util/flash');

    var QUESTION_SELECTOR = '.question';
    var ANSWER_SELECTOR = '.answer-choice';
    var ANSWER_LIST_SELECTOR = '.answer-list';

    var attachInteractions = function () {
        var self = this;

        //We have to do this first so that it overrides the general question-box click below
        this.ui.streamList.on('click', ANSWER_SELECTOR, function (e) {
            answerQuestion.call(self, $(this));

            //Prevent propagation to the background
            e.preventDefault();
            return false;
        });

        this.ui.streamList.on('click', QUESTION_SELECTOR, function (e) {
            //Expand the answer list
            toggleQuestion.call(self, $(this));
        });

    }

    var toggleQuestion = function (question, toggle) {
        if (question.is('.disabled')) {
            return;
        }

        if (typeof toggle === 'undefined') {
            question.find(ANSWER_LIST_SELECTOR).collapse('toggle');
        } else if (toggle) {
            question.find(ANSWER_LIST_SELECTOR).collapse('show');
        } else {
            question.find(ANSWER_LIST_SELECTOR).collapse('hide');
        }

        question.toggleClass('activated', toggle);

        if (question.is('.activated')) {
            //Calculate the height of the question, once expanded
            var height = question.height();
            question.find('.answer-choice').each(function () {
                height += $(this).outerHeight(true);
            });

            //Get the amount we need to scroll by
            var top = question.offset().top - $(window).scrollTop()
            var bottom = top + height;

            //Buffers of 10px
            var viewTop = $('.navbar').height() + 10;
            var viewBottom = $(window).height() - 10;

            var newTop = top;
            if (top < viewTop) {
                newTop = viewTop;
            } else if (bottom > viewBottom) {
                //Slide up so the bottom is on screen, but don't push the top out
                newTop = Math.max(viewTop, viewBottom - height);
            }

            if (newTop != top) {
                $('html, body').animate({
                    scrollTop: question.offset().top - newTop
                }, 400);
            }
        }
    }

    var fillQuestionModal = function (question) {
        question = question.clone();

        //Extract the question subject because it is awkwardly placed
        var subject = question.find('.question-subject');
        question.find('.question-body').prepend(subject);

        //Move the header to the bottom (it just has the pic)
        var header = question.find('.question-header');
        question.find('.question-body').after(header);

        //Make the buttons button-ey
        question.find('.answer-choice')
            .addClass('btn');

        this.ui.questionWrapper.html(question);
    }

    var answerQuestion = function (answer) {
        var self = this;
        var question = answer.parents('.question');

        if (question.is('.disabled')) {
            return;
        }

        question.addClass('disabled');

        var oldAnswer = question.find('.selected');
        setSelectedAnswer(question, answer);

        var requestUrl = url.extend('answer');
        var data = {
            id: question.data('id'),
            answer: $.trim(answer.html())
        };

        var request = $.post(requestUrl, data);
        request.done(function (response) {
            flash.success(response);
            question.addClass('answered');
            question.removeClass('disabled');
            toggleQuestion.call(self, question, false);
        });
        request.error(function (xhr) {
            flash.error(xhr.responseText);
            setSelectedAnswer(question, oldAnswer);
            question.data('mid-answer', false);
            question.removeClass('disabled');
        });
    }

    var setSelectedAnswer = function(question, answer) {
        question.find('.selected').removeClass('selected');
        answer.addClass('selected');
    }

    var QuestionBox = function () {
        attachInteractions.call(this);
        // catchSubmit.call(this);
    }

    return QuestionBox;
});