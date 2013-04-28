define(function(require) {

    var $ = require('jquery');
    var url = require('util/url');
    var flash = require('util/flash');

    var QUESTION_SELECTOR = '.question';
    var ANSWER_SELECTOR = '.answer-choice';
    var ANSWER_LIST_SELECTOR = '.answer-list';

    var attachInteractions = function() {
        var self = this;

        //We have to do this first so that it overrides the general question-box click below
        this.ui.streamList.on('click', ANSWER_SELECTOR, function(e) {
            answerQuestion.call(self, $(this));

            //Prevent propagation to the background
            e.preventDefault();
            return false;
        });

        this.ui.streamList.find(ANSWER_LIST_SELECTOR)
            //We already have css to hide the box, but this will let the collapse plugin function later
            .addClass('collapse');

        this.ui.streamList.on('click', QUESTION_SELECTOR, function(e) {
            //Expand the answer list
            toggleQuestion.call(self, $(this));
        });

    }

    var toggleQuestion = function(question, toggle) {
        if (typeof toggle === 'undefined') {
            question.find(ANSWER_LIST_SELECTOR).collapse('toggle');
        } else if (toggle) {
            question.find(ANSWER_LIST_SELECTOR).collapse('show');
        } else {
            question.find(ANSWER_LIST_SELECTOR).collapse('hide');
        }
    }

    var fillQuestionModal = function(question) {
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

    var answerQuestion = function(answer) {
        var self = this;
        var question = answer.parents('.question');

        var requestUrl = url.extend('answer');
        var data = {
            id: question.data('id'),
            answer: $.trim(answer.html())
        };

        var request = $.post(requestUrl, data);
        request.done(function(response) {
            flash.success(response);
            toggleQuestion.call(self, question, false);
        });
        request.error(function(xhr) {
            flash.error(xhr.responseText);
        });
    }

    var QuestionBox = function() {
        attachInteractions.call(this);
        // catchSubmit.call(this);
    }

    return QuestionBox;
});