define(function(require) {

    var $ = require('jquery');
    var url = require('util/url');
    var flash = require('util/flash');

    var QUESTION_SELECTOR = '.question';
    var ANSWER_SELECTOR = '.answer-choice';

    var attachInteractions = function() {
        var self = this;

        this.ui.streamList.on('click', QUESTION_SELECTOR, function(e) {
            fillQuestionModal.call(self, $(this));
            self.ui.questionBox.modal('show');
        });

        this.ui.questionBox.on('click', ANSWER_SELECTOR, function(e) {
            answerQuestion.call(self, $(this));
        });

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
            self.ui.questionBox.modal('hide');
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