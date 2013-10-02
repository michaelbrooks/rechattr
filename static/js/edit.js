define(function(require) {

    var $ = require('jquery');
    require('vendor/bootstrap');
    var flash = require('util/flash');
    var url = require('util/url');

    //Turn off []-appending to posted arrays
    //More: http://forum.jquery.com/topic/jquery-post-1-4-1-is-appending-to-vars-when-posting-from-array-within-array
    $.ajaxSettings.traditional = true;

    var TIME_FORMAT = 'h:mma';
    var DATE_FORMAT = 'M/DD/YYYY';
    
    var INTERVAL_FIELD_SELECTOR = '.interval-field';
    
    //var TIMELINE_WRAPPER_SELECTOR = '.timeline-wrapper';
    var QUESTION_LIST_SELECTOR = '.question-list';
    var QUESTION_SELECTOR = '.question';
    
    var NEW_QUESTION_BUTTON_SELECTOR = '.new-question-button';
    var QUESTION_DELETE_SELECTOR = '.question-delete';
    
    var EditApp = function() {
        var self = this;
        
        this.initUI();
        this.attachEvents();
        
        flash.initFlash();

        // this.timeline = new rechattr.util.Timeline(this.ui.timelineWrapper);
        
        // this.attachTimelineEvents();
        
        // this.initQuestionList(); 
    };
    
    EditApp.prototype.initUI = function() {
        this.ui = {};
        
        //this.ui.timelineWrapper = $(TIMELINE_WRAPPER_SELECTOR);
        this.ui.intervalField = $(INTERVAL_FIELD_SELECTOR);
        this.ui.questionList = $(QUESTION_LIST_SELECTOR);
        this.ui.newQuestionButton = $(NEW_QUESTION_BUTTON_SELECTOR);
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
    };

    EditApp.prototype.deleteQuestion = function(question) {
        var id = question.data('id');

        $.ajax({
            url: url.poll('questions', id),
            type: 'DELETE'
        })
            .done(function(response) {
                flash.success('Question deleted');
                question.one('hidden', function() {
                    question.remove();
                });
                question.collapse('hide');
            })
            .error(function(xhr) {
                flash(xhr.responseText);
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
            .fail(function() {
                flash.error('Failed to add a question. Please refresh and try again.');
            });
    };

    EditApp.prototype.insertQuestion = function(questionHtml) {
        var questionElement = $(questionHtml)
            .appendTo(this.ui.questionList);

        //TODO: Build apply the question behavior to the question element
    };

    EditApp.prototype.showEditor = function(question) {

        var self = this;

        if (this.editor.isEditing(question)) {
            return;
        }

        //if already showing, hide first
        if (this.editor.isShowing()) {
            this.hideEditor();

            this.editor.ui.el.one('hidden', function() {
                self.showEditor(question);
            });

            return;
        }

        this.editor.blank();

        //Determine where in the question list the form should go
        if (question) {
            //Fill the editor with content
            this.editor.fill(question);
            //Position the editor
            question.after(this.editor.ui.el);
        } else {
            //Just need a blank editor
            this.ui.questionList.prepend(this.editor.ui.el);
        }

        this.editor.show(question);
        if (question) {
            question.collapse('hide');
        }
    };
    
    EditApp.prototype.hideEditor = function() {
        if (this.editor.currentQuestion) {
            this.editor.currentQuestion.collapse('show');
        }
        this.editor.hide();
    };
    
//    EditApp.prototype.initQuestionList = function() {
//        var questionElements = this.ui.questionList.find(QUESTION_SELECTOR);
//        var self = this;
//        questionElements.each(function(index, element) {
//            var question = new Question($(element));
//            var bead = self.ui.timelineWrapper.find('.timeline-bead[data-id=' + question.data.id + ']');
//            self.bindQuestion(question, bead);
//        });
//    };
//
//    EditApp.prototype.bindQuestion = function(question, bead) {
//        var self = this;
//
//        $(question).on('delete', function() {
//            self.timeline.deleteBead(bead);
//        });
//
//        bead.data('question', question);
//    };
//
//    EditApp.prototype.attachTimelineEvents = function() {
//        var self = this;
//        $(this.timeline).on('new-bead', function(e, bead, percentThrough) {
//
//            var question = new Question();
//            question.offsetSeconds(percentThrough * self.model.duration);
//
//            self.bindQuestion(question, bead);
//
//            self.ui.questionList.append(question.render());
//            question.save();
//        })
//        .on('select', function(e, bead) {
//            var question = bead.data('question');
//            question.message = 'yay';
//            question.render();
//        })
//        .on('deselect', function(e, bead) {
//            var question = bead.data('question');
//            question.message = 'aw...';
//            question.render();
//        });
//    }

    window.app = new EditApp();
    return window.app;
});