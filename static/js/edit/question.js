define(function(require) {
    var $ = require('jquery');
    var flash = require('util/flash');
    var url = require('util/url');

    /**
     * Todo: This may be obsolete.
     * @param element
     * @constructor
     */
    var Question = function(element) {
        if (element) {
            this.$el = element;
            this.extractData(element);
        } else {
            this.initDefaultData();
            this.$el = $('<div>').addClass('question');
            this.initUI();
        }

        this.attachEvents();
    }

    Question.prototype.extractData = function(element) {
        this.initUI();

        this.data = {};
        this.data.id = this.$el.data('id');
        this.data.subject = this.ui.subject.data('subject');
        this.data.question_text = this.ui.question_text.data('question_text');
        this.data.answer_choices = [];
        var self = this;
        this.ui.answer_choices.children().each(function(index, choice) {
            self.data.answer_choices.push(choice.html());
        });

        this.data.trigger_type = this.$el.data('trigger_type');
        this.data.trigger_info = this.ui.trigger_info.data('trigger_info');
    }

    Question.prototype.initDefaultData = function() {
        this.data = {};
        this.data.subject = "Magnets";
        this.data.question_text = "How do they work?";
        this.data.answer_choices = ['well','badly'];
        this.data.trigger_type = 'time_offset';
        this.data.trigger_info = 0;
    }

    Question.prototype.updateModel = function(data) {
        this.data.subject = data.subject;
        this.data.question_text = data.question_text;
        // this.data.answer_choices =
    }

    Question.prototype.offsetSeconds = function(seconds) {
        this.data.trigger_info = seconds;
    }

    Question.prototype.formError = function(formElement, message) {
        formElement.parents('.control-group').addClass('error');
        formElement.focus();
        flash.error(message);
    }

    Question.prototype.formSuccess = function(formElement) {
        this.$el.find('.control-group').removeClass('error');
    }

    Question.prototype.save = function() {
        var self = this;
        $.post('', this.data)
        .done(function(response) {
            if (response.type == 'error') {
                var element = self.ui[response.about];
                self.formError(element, response.message);
            } else if (response.type == 'success') {
                self.formSuccess();

                self.updateModel(response.question);
            }
        })
        .error(function(response) {
            console.log(response);
            flash(response);
        });
    }

    Question.prototype.deleteQuestion = function() {
        var self = this;

        var deleteMe = function() {
            $(self).trigger('delete');
            self.$el.remove();
        }

        $.ajax({
            url: url.extend('question', this.data.id),
            type: 'DELETE',
            data: {question: this.data.id}
        })
        .done(function(response) {
            if (response.type == 'error') {
                flash.error(response.message)
            } else if (response.type == 'success') {
                deleteMe();
            }
        })
        .error(function(response) {
            console.log(response);
            flash(response);
        });
    }

    Question.prototype.initUI = function() {
        this.ui = {};
        this.ui.subject = this.$el.find(QUESTION_SUBJECT_SELECTOR);
        this.ui.question_text = this.$el.find(QUESTION_TEXT_SELECTOR);
        this.ui.answer_choices = this.$el.find(QUESTION_ANSWER_LIST_SELECTOR);
        this.ui.trigger_info = this.$el.find(QUESTION_INFO_SELECTOR);
        this.ui.deleteButton = this.$el.find(QUESTION_DELETE_SELECTOR);
    }

    Question.prototype.render = function() {
        this.$el.html(this.template(this.data));

        this.initUI()

        return this.$el;
    }

    Question.prototype.attachEvents = function() {
        this.$el.on('click', QUESTION_DELETE_SELECTOR, $.proxy(this.deleteQuestion, this));
    }
});