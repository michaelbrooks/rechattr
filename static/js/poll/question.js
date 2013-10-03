define(function (require) {

    var $ = require('jquery');
    var url = require('util/url');
    var flash = require('util/flash');
    var overlay = require('util/overlay');

    var QUESTION_SELECTOR = '.question';
    var ANSWER_LIST_SELECTOR = '.answer-list';
    var REPLY_BUTTON_SELECTOR = '.reply-button';

    var Question = function(questionWrapper) {
        this.container = questionWrapper;

        this.attachEvents();
    };

    Question.prototype.attachEvents = function() {
        var self = this;

        this.container.on('change', 'input[type=radio]', function() {
            //When an answer is clicked
            self.submit();
        });

        this.container.on('click', REPLY_BUTTON_SELECTOR, function() {
            console.log("replying...");
        });
    };

    Question.prototype.submit = function() {
        var self = this;

        var question = this.container.find(QUESTION_SELECTOR);
        var value = this.container.find('input:checked').val();

        var requestUrl = url.poll('answer');

        var data = {
            question: question.data('id'),
            answer: value
        };

        overlay.showLoading(self.container);

        var request = $.ajax({
            url: requestUrl,
            data: data,
            type: "POST"
        })
            .done(function (response) {
                self.container.html(response);
            })
            .fail(function (xhr) {
                flash.error(xhr.statusText);
                if (xhr.responseText) {
                    self.container.html(xhr.responseText);
                }
            })
            .always(function() {
                overlay.hide(self.container);
            });
    };

    return Question;
});
