(function() {

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
        
        rechattr.util.initFlash();

        // this.timeline = new rechattr.util.Timeline(this.ui.timelineWrapper);
        
        // this.attachTimelineEvents();
        
        // this.initQuestionList(); 
    }
    
    EditApp.prototype.initUI = function() {
        this.ui = {};
        
        //this.ui.timelineWrapper = $(TIMELINE_WRAPPER_SELECTOR);
        this.ui.intervalField = $(INTERVAL_FIELD_SELECTOR);
        this.ui.questionList = $(QUESTION_LIST_SELECTOR);
        this.ui.newQuestionButton = $(NEW_QUESTION_BUTTON_SELECTOR);

        //Build the editor
        this.editor = new rechattr.util.Editor();
    }


    EditApp.prototype.attachEvents = function() {
        var self = this;

        this.ui.newQuestionButton.on('click', function(e) {
            self.showEditor(null)
        });

        this.ui.questionList.on('click', QUESTION_DELETE_SELECTOR, function(e) {
            self.deleteQuestion($(this).parents(QUESTION_SELECTOR));
            e.preventDefault();
            return false;
        });

        //When a question is clicked, invoke the editor for that question
        this.ui.questionList.on('click', QUESTION_SELECTOR, function(e) {
            self.showEditor($(this));
        });

        this.editor.on('cancel', function(e) {
            self.hideEditor();
        });

        this.editor.on('new-question', function(e, questionHtml) {
            self.ui.questionList.append(questionHtml);
        });


    };

    EditApp.prototype.deleteQuestion = function(question) {
        var id = question.data('id');

        $.ajax({
            url: rechattr.util.url.extend('question', id),
            type: 'DELETE'
        })
            .done(function(response) {
                rechattr.util.flash.success('Question deleted');
                question.one('hidden', function() {
                    question.remove();
                });
                question.collapse('hide');
            })
            .error(function(xhr) {
                console.log('Error deleting question', xhr);
                rechattr.util.flash(xhr.responseText);
            });
    }

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
    
    EditApp.prototype.initQuestionList = function() {
        var questionElements = this.ui.questionList.find(QUESTION_SELECTOR);
        var self = this;
        questionElements.each(function(index, element) {
            var question = new Question($(element));
            var bead = self.ui.timelineWrapper.find('.timeline-bead[data-id=' + question.data.id + ']');
            self.bindQuestion(question, bead);
        });
    };
    
    EditApp.prototype.bindQuestion = function(question, bead) {
        var self = this;
        
        $(question).on('delete', function() {
            self.timeline.deleteBead(bead);
        });
        
        bead.data('question', question);
    };
    
    EditApp.prototype.attachTimelineEvents = function() {
        var self = this;
        $(this.timeline).on('new-bead', function(e, bead, percentThrough) {
            
            var question = new Question();
            question.offsetSeconds(percentThrough * self.model.duration);
            
            self.bindQuestion(question, bead);
            
            self.ui.questionList.append(question.render());
            question.save();
        })
        .on('select', function(e, bead) {
            var question = bead.data('question');
            question.message = 'yay';
            question.render();
        })
        .on('deselect', function(e, bead) {
            var question = bead.data('question');
            question.message = 'aw...';
            question.render();
        });
    }

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
        rechattr.util.flash.error(message);
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
            rechattr.util.flash(response);
        });
    }
    
    Question.prototype.deleteQuestion = function() {
        var self = this;
        
        var deleteMe = function() {
            $(self).trigger('delete');
            self.$el.remove();
        }
        
        $.ajax({
            url: rechattr.util.url.extend('question', this.data.id),
            type: 'DELETE',
            data: {question: this.data.id}
        })
        .done(function(response) {
            if (response.type == 'error') {
                rechattr.util.flash.error(response.message)
            } else if (response.type == 'success') {
                deleteMe();
            }
        })
        .error(function(response) {
            console.log(response);
            rechattr.util.flash(response);
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
    
    rechattr.classes.EditApp = EditApp;
    return EditApp;
})()