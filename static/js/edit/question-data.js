define(function(require) {

    var url = require('util/url');

    var SUBJECT_INPUT_SELECTOR = '.question-subject';
    var TEXT_INPUT_SELECTOR = '.question-text';
    var ANSWER_LIST_SELECTOR = '.answer-list';
    var IMAGE_SELECTOR = '.question-image';

    //An object that collects data from the question display
    var QuestionData = function(question) {
        this.data = {
            subject: "",
            question_text: "",
            image_src: "",
            trigger_manual: false,
            trigger_seconds: null,
            answer_choices: []
        }
        this.dirty = false;

        if (question) {
            this.question = question;
            this.data.id = question.data('id');
            this.data.trigger_manual = question.data('trigger-manual');

            var seconds = question.data('trigger-seconds');
            if (seconds) {
                this.data.trigger_seconds = Number(seconds);
            } else {
                this.data.trigger_seconds = null
            }

            this.data.subject = question.find(SUBJECT_INPUT_SELECTOR).text();
            this.data.question_text = question.find(TEXT_INPUT_SELECTOR).text();
            this.data.image_src = question.find(IMAGE_SELECTOR).attr('src');
            var answerList = question.find(ANSWER_LIST_SELECTOR);
            var answers = this.data.answer_choices;

            answerList.children().each(function(index, listElement) {
                var contents = $(listElement).html();
                answers.push($.trim(contents));
            });

            this._json_answers = JSON.stringify(answers);
        }
    };
//
//    QuestionData.prototype.updateQuestion = function() {
//        if (!this.question) {
//            return;
//        }
//
//        this.question.data('id', this.data.id);
//        this.question.find(SUBJECT_INPUT_SELECTOR).text(this.data.subject);
//        this.question.find(TEXT_INPUT_SELECTOR).text(this.data.question_text);
//        this.question.find(IMAGE_SELECTOR).attr('src', this.data.image_src);
//
//        var answerList = this.question.find(ANSWER_LIST_SELECTOR);
//        answerList.empty();
//
//        var self = this;
//        $.each(this.data.answer_choices, function(i, value) {
//            value = self.choice(value);
//            answerList.append(value);
//        });
//    }

    QuestionData.prototype.set = function(member, value) {
        if (member in this.data) {
            var changed = value !== this.data[member];
            if ($.isArray(value)) {
                changed = this._json_answers !== JSON.stringify(value);
            }

            if (changed) {
                this.data[member] = value;
                this.dirty = true;
            }
        } else {
            throw 'Data "' + member + '" not defined';
        }
    }

    QuestionData.prototype.get = function(member) {
        if (member in this.data) {
            return this.data[member];
        } else {
            throw 'Data "' + member + '" not defined';
        }
    }

    QuestionData.prototype.submit = function() {
        var self = this;

        var urlStr = url.extend('question', this.data.id);
        return $.post(urlStr, this.data)
            .done(function (response) {
                self.dirty = false;
            })
            .error(function (response) {
                console.log('Error submitting question', response);
            });
    }

    QuestionData.prototype.choice = function(answerHtml) {
        //Generate an answer icon
        var answer = $(answerHtml);

        var listItem = $('<li>')
            .addClass('answer-choice')
            .append(answer);

        //Editable if a text value
        if (answer.is('.value')) {
            listItem.addClass('editable');
        }

        return listItem;
    };

    return QuestionData;
});