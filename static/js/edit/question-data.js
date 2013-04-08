(function() {

    var SUBJECT_INPUT_SELECTOR = '.question-subject';
    var TEXT_INPUT_SELECTOR = '.question-text';
    var ANSWER_LIST_SELECTOR = '.answer-list';
    var IMAGE_SELECTOR = '.question-image';
    var ANSWER_VALUE_SELECTOR = '.value';

    //An object that collects data from the question display
    var QuestionData = function(question) {
        this.data = {
            subject: "",
            question_text: "",
            image_src: "",
            trigger_type: 'time_offset',
            trigger_info: 0,
            answer_choices: []
        }
        this.dirty = false;

        if (question) {
            this.question = question;
            this.data.id = question.data('id');
            this.data.trigger_type = question.data('trigger-type');
            this.data.trigger_info = question.data('trigger-info');

            this.data.subject = question.find(SUBJECT_INPUT_SELECTOR).text();
            this.data.question_text = question.find(TEXT_INPUT_SELECTOR).text();
            this.data.image_src = question.find(IMAGE_SELECTOR).attr('src');
            var answerList = question.find(ANSWER_LIST_SELECTOR);
            var answers = this.data.answer_choices;

            answerList.children().each(function(index, listElement) {
                var contents = $(listElement).find(ANSWER_VALUE_SELECTOR).html();
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

        var url = rechattr.util.url.extend('question', this.data.id);
        return $.post(url, this.data)
            .done(function (response) {
                self.dirty = false;
            })
            .error(function (response) {
                console.log('Error submitting question', response);
            });
    }

    QuestionData.prototype.choice = function(answerHtml) {
        //Generate an answer icon
        var answer = $('<div>')
            .addClass('value')
            .html($.trim(answerHtml));

        var listItem = $('<li>')
            .addClass('answer-choice')
            .html(answer);

        //Editable if nothing but text children
        if (answer.children().size() == 0) {
            listItem.addClass('editable');
        }

        //Image button if contains an image
        if (answer.find('img').size() > 0) {
            listItem.addClass('img');
        }

        return listItem;
    };


    rechattr.util.QuestionData = QuestionData;
    return QuestionData;
})();