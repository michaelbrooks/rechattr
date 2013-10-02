define(function(require) {

    var $ = require('jquery');
    var url = require('util/url');
    var events = require('util/events');
    var flash = require('util/flash');
    var dtutils = require('util/dtutils');
    var moment = require('moment');
    var overlay = require('util/overlay');

    var QUESTION_SELECTOR = '.question-editor';
    var TEXT_INPUT_SELECTOR = '.question-text';
    var ANSWER_LIST_SELECTOR = '.question-answers';
    var TRIGGER_TIME_SELECTOR = '.trigger-time';
    var TRIGGER_OFFSET_SELECTOR = '.trigger-offset';

    //An object that collects data from the question display
    //The questionContainerElement is a element containing a .question-editor
    var Question = function(questionContainerElement) {
        this.ui = questionContainerElement;

        this.initEvents();
    };

    Question.prototype.initEvents = function() {
        var self = this;

        this.ui.on('change', TRIGGER_TIME_SELECTOR, function() {
            if (self.updateTimingData($(this))) {
                self.submit();
            }
        });

        this.ui.on('change', TRIGGER_OFFSET_SELECTOR, function(e) {
            if (self.updateTimingData($(this))) {
                self.submit();
            }
        });

        this.ui.on('change', TEXT_INPUT_SELECTOR, function(e) {
            self.submit();
        });

        this.ui.on('change', ANSWER_LIST_SELECTOR, function(e) {
            self.submit();
        });
    };

    Question.prototype.updateTimingData = function (valueSourceElement) {
        var question = this.ui.find(QUESTION_SELECTOR);

        var value = $.trim(valueSourceElement.val());

        var seconds;
        if (valueSourceElement.is(TRIGGER_OFFSET_SELECTOR)) {
            seconds = dtutils.offset.parse(value);
        } else {
            var start = moment(question.data('event-start'));
            seconds = question.data('trigger-seconds');

            var trigger = start.clone();
            trigger.add('seconds', seconds);

            var time = dtutils.time.parse(value);
            if (time === false) {
                return false;
            }

            trigger.hour(time.hour);
            trigger.minute(time.minute);

            seconds = trigger.diff(start, 'seconds');
        }

        if (value.length > 0 && seconds === null) {
            flash.error('Value ' + value + ' could not be parsed!');
            return false;
        } else {
            //Save it for submitting
            question.data('trigger-seconds', seconds);
            return true;
        }
    };

    Question.prototype.collect = function() {
        var data = {
            question_text: "",
            image_src: "",
            trigger_manual: false,
            trigger_seconds: null,
            answer_choices: ''
        };

        var question = this.ui.find(QUESTION_SELECTOR);

        data.id = question.data('id');
        data.trigger_manual = question.data('trigger-manual');
        data.trigger_seconds = question.data('trigger-seconds');

        data.question_text = question.find(TEXT_INPUT_SELECTOR).val();

        data.answer_choices = question.find(ANSWER_LIST_SELECTOR).val();

        return data;
    };

    Question.prototype.submit = function() {
        var self = this;

        //Scrape the data from the form
        var data = this.collect();
        var urlStr = url.poll('questions', data.id);

        this.ui.find('input,textarea').prop('disabled', true);
        overlay.showLoading(this.ui);

        return $.ajax({
            url: urlStr,
            type: 'PUT',
            data: data
        })
            .done(function (response) {
                self.ui.html(response);
            })
            .fail(function (xhr) {
                flash.error(xhr.statusText);
                if (xhr.responseText) {
                    self.ui.html(xhr.responseText);
                }
            })
            .always(function() {
                overlay.hide(self.ui);
                if (!this.ui.find(QUESTION_SELECTOR).is('.triggered')) {
                    self.ui.find('input,textarea').prop('disabled', false);
                }
            });
    };

    events(Question);

    return Question;
});