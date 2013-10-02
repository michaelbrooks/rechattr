define(function(require) {

    var $ = require('jquery');
    require('vendor/bootstrap');
    var flash = require('util/flash');
    var url = require('util/url');

    var Question = require('edit/question');
    var IntervalSelection = require('modules/interval-selection');

    //Turn off []-appending to posted arrays
    //More: http://forum.jquery.com/topic/jquery-post-1-4-1-is-appending-to-vars-when-posting-from-array-within-array
    $.ajaxSettings.traditional = true;

    var TIME_FORMAT = 'h:mma';
    var DATE_FORMAT = 'M/DD/YYYY';
    
    var INTERVAL_FIELD_SELECTOR = '.interval-field';
    
    //var TIMELINE_WRAPPER_SELECTOR = '.timeline-wrapper';
    var QUESTION_LIST_SELECTOR = '.question-list';
    var QUESTION_SELECTOR = '.question-editor';
    
    var NEW_QUESTION_BUTTON_SELECTOR = '.new-question-button';
    var QUESTION_DELETE_SELECTOR = '.question-delete';
    var POLL_EDITOR_SELECTOR = '.poll-editor';

    var EditApp = function() {
        var self = this;
        
        this.initUI();
        this.attachEvents();
        
        flash.initFlash();

        this.initQuestionList();

        this.intervalSelector = new IntervalSelection($(INTERVAL_FIELD_SELECTOR));
    };
    
    EditApp.prototype.initUI = function() {
        this.ui = {};
        
        //this.ui.timelineWrapper = $(TIMELINE_WRAPPER_SELECTOR);
        this.ui.intervalField = $(INTERVAL_FIELD_SELECTOR);
        this.ui.questionList = $(QUESTION_LIST_SELECTOR);
        this.ui.newQuestionButton = $(NEW_QUESTION_BUTTON_SELECTOR);
        this.ui.pollEditor = $(POLL_EDITOR_SELECTOR);
        this.ui.pollSubmitButton = this.ui.pollEditor.find('.submit-button');
    };


    EditApp.prototype.attachEvents = function() {
        var self = this;

        this.ui.newQuestionButton.on('click', function(e) {
            self.addQuestion();
        });

        this.ui.questionList.on('click', QUESTION_DELETE_SELECTOR, function(e) {
            var questionElement = $(this).parents(QUESTION_SELECTOR);
            self.deleteQuestion(questionElement);

            e.preventDefault();
            return false;
        });

        this.ui.pollEditor.on('change', function() {
            self.ui.pollSubmitButton
                .prop('disabled', false)
                .addClass('in');
        });
    };

    EditApp.prototype.deleteQuestion = function(questionElement) {
        var self = this;

        var id = questionElement.data('id');

        $.ajax({
            url: url.poll('questions', id),
            type: 'DELETE'
        })
            .done(function(response) {
                self.removeQuestion(questionElement);
            })
            .fail(function(xhr) {
                flash.error(xhr.responseText);
            });
    };

    EditApp.prototype.addQuestion = function() {
        var self = this;

        $.ajax({
            url: url.poll('questions'),
            type: 'POST'
        })
            .done(function(response) {
                self.insertQuestion(response);
            })
            .fail(function(xhr) {
                flash.error(xhr.responseText);
            });
    };

    EditApp.prototype.insertQuestion = function(questionHtml) {
        var questionElement = $(questionHtml);
        var questionWrapper = $('<div>')
            .append(questionElement)
            .addClass("collapse")
            .appendTo(this.ui.questionList)
            .collapse('show');

        $('html, body').animate({
            scrollTop: questionElement.offset().top
        }, 500);

        this.addQuestionEvents(questionWrapper);
    };

    EditApp.prototype.removeQuestion = function(questionElement) {
        var wrapper = questionElement.parent();
        //Listen for the collapse's end event
        wrapper.one('hidden', function() {
            wrapper.remove();
        });
        wrapper.collapse('hide');
    };

    EditApp.prototype.initQuestionList = function() {
        var self = this;
        this.ui.questionList.children().each(function() {
            self.addQuestionEvents($(this));
        });
    };

    EditApp.prototype.addQuestionEvents = function(questionWrapper) {
        var question = new Question(questionWrapper);
    };

    window.app = new EditApp();
    return window.app;
});