(function() {

    var TIME_FORMAT = 'h:mma';
    var DATE_FORMAT = 'M/DD/YYYY';
    
    //var EVENT_TIMING_SELECTOR = '.event-timing';
    
    //var TIMELINE_WRAPPER_SELECTOR = '.timeline-wrapper';
    var QUESTION_LIST_SELECTOR = '.question-list';
    var QUESTION_SELECTOR = '.question';
    
    var QUESTION_EDITOR_SELECTOR = '.question-editor';
    var EDITOR_PREV_BUTTON_SELECTOR = '.prev-button';
    var EDITOR_NEXT_BUTTON_SELECTOR = '.next-button';

    var QUESTION_SUBJECT_SELECTOR = '.question-subject';
    var QUESTION_TEXT_SELECTOR = '.question-text';
    var QUESTION_ANSWER_LIST_SELECTOR = '.answer-list';
    var QUESTION_IMAGE_SELECTOR = '.question-image';
    var QUESTION_IMAGE_INPUT_SELECTOR = '.question-image-input';
    
    var ANSWER_PALETTE_SELECTOR = '.answer-palette';
    var ANSWER_CHOICE_SELECTOR = '.answer-choice';
    var ANSWER_VALUE_SELECTOR = '.value';
    var EDITABLE_VALUE_SELECTOR = '.editable';

    var ANSWER_CHOICES_INPUT_SELECTOR = '.answer-choices';
    var ANSWER_EDITOR_SELECTOR = '.answer-editor';
    var NEW_QUESTION_BUTTON_SELECTOR = '.new-question-button';
    var QUESTION_SAVE_SELECTOR = '.question-save';
    var QUESTION_CANCEL_SELECTOR = '.question-save';
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
        //this.ui.eventTiming = $(EVENT_TIMING_SELECTOR);
        this.ui.questionList = $(QUESTION_LIST_SELECTOR);
        this.ui.newQuestionButton = $(NEW_QUESTION_BUTTON_SELECTOR);
        
        var editor = this.ui.editor = $(QUESTION_EDITOR_SELECTOR);
        this.ui.editorPaletteNext = editor.find(EDITOR_NEXT_BUTTON_SELECTOR);
        this.ui.editorPalettePrev = editor.find(EDITOR_PREV_BUTTON_SELECTOR);

        this.ui.editorForm = editor.find('form');
        this.ui.editorSubject = editor.find(QUESTION_SUBJECT_SELECTOR);
        this.ui.editorText = editor.find(QUESTION_TEXT_SELECTOR);
        this.ui.editorImage = editor.find(QUESTION_IMAGE_SELECTOR);
        this.ui.editorImageInput = editor.find(QUESTION_IMAGE_INPUT_SELECTOR);
        this.ui.answerPalette = editor.find(ANSWER_PALETTE_SELECTOR);
        this.ui.answerPaletteItems = this.ui.answerPalette.find('ul');
        this.ui.editorAnswersList = editor.find(QUESTION_ANSWER_LIST_SELECTOR);
        this.ui.editorAnswersInput = editor.find(ANSWER_CHOICES_INPUT_SELECTOR);
        
        this.ui.editorSave = editor.find(QUESTION_SAVE_SELECTOR);
        this.ui.editorCancel = editor.find(QUESTION_CANCEL_SELECTOR);
    }

    EditApp.prototype.shiftPalette = function(by) {
        //Get the palette container width
        var width = this.ui.answerPalette.width();

        //Get the current relative offset
        var offset = this.ui.answerPaletteItems.position().left;
        var maxShift = this.ui.answerPaletteItems.width() - width;

        var shift = offset - by * width * 0.9;

        //Shift must be between -width and 0
        shift = Math.min(0, Math.max(-maxShift, shift));
        this.ui.answerPaletteItems.css('left', shift + 'px');

        if (shift == -maxShift) {
            this.ui.editorPaletteNext.attr('disabled', 'disabled');
        } else {
            this.ui.editorPaletteNext.removeAttr('disabled');
        }

        if (shift == 0) {
            this.ui.editorPalettePrev.attr('disabled', 'disabled');
        } else {
            this.ui.editorPalettePrev.removeAttr('disabled');
        }
    }

    EditApp.prototype.attachEvents = function() {
        var self = this;

        this.ui.editorPaletteNext.on('click', function(e) {
            self.shiftPalette(1);
        });

        this.ui.editorPalettePrev.on('click', function(e) {
            self.shiftPalette(-1);
        });

        this.ui.newQuestionButton.on('click', function(e) {
            self.showEditor()
        });
        
        //When a question is clicked, invoke the editor for that question
        this.ui.questionList.on('click', QUESTION_SELECTOR, function(e) {
            self.showEditor($(this));
        });
        
        // this.ui.answerPalette.on('mousedown', function(e) {
            // var offset = self.ui.answerPaletteList.position();
            // self.startingMousePos = e.pageX;
            // self.dragDisplacement = offset.left;
            // self.dragMax = self.ui.answerPaletteList.width();
            // debugger;
        // })
        // .on('mousemove', function(e) {
            // if (self.dragDisplacement) {
                // var change = e.pageX - self.startingMousePos;
                // var displacement = self.dragDisplacement + change;
                // console.log(change, displacement);
                // if (displacement > 0) {
                    // displacement = 0;
                // }
                // self.ui.answerPaletteList.css('left', (displacement) + 'px');
            // }
        // });
        // $(document).on('mouseup', function(e) {
            // self.dragDisplacement = false;
        // });
        
        this.ui.answerPalette.on('click', ANSWER_CHOICE_SELECTOR, function(e) {
            var answerValue = $(this).find(ANSWER_VALUE_SELECTOR)
            self.addAnswerChoice(answerValue.html())
        });

        this.ui.editorAnswersList.on('click', ANSWER_CHOICE_SELECTOR, function(e) {
            if (self.engageAnswerEditor($(this))) {
                e.preventDefault();
                return false;
            } else {
                //The answer editor was not engaged. Uneditable.
            }
        });

        this.ui.editorAnswersList.on('keyup', ANSWER_EDITOR_SELECTOR, function(e) {
            self.captureEditorValue($(this));
        });

        this.ui.editorAnswersList.on('keydown', ANSWER_EDITOR_SELECTOR, function(e) {
            //Catch enter presses
            if (e.which == 13) {
                e.preventDefault();

                //self.disengageAnswerEditor($(this));
                $(this).blur();
                return false;
            }
        });

        this.ui.editorAnswersList.on('blur', ANSWER_EDITOR_SELECTOR, function(e) {
            self.disengageAnswerEditor($(this));
        });

        this.ui.editorAnswersList.dragsort({
            dragSelector: 'li',
            dragEnd: function() {
                self.collectAnswers($(this));
            }
        });
    };

    EditApp.prototype.engageAnswerEditor = function(answer) {
        if (answer.is('.editing')) {
            return;
        }

        var answerValue = answer.find(EDITABLE_VALUE_SELECTOR);

        //Editable if the value is straight text
        if (answerValue.size()) {
            answer.addClass('editing');

            var value = answerValue.html();
            var input = $('<input>')
                .attr('type', 'text')
                .addClass('answer-editor')
                .val(value);

            answer.append(input);

            input.focus();

            return true;
        }
    }

    EditApp.prototype.captureEditorValue = function(editor) {
        //Update the answer value from the input element
        var value = editor.val();
        var valueBox = editor.parent().find(ANSWER_VALUE_SELECTOR);
        valueBox.text(value);
    }

    EditApp.prototype.disengageAnswerEditor = function(editor) {
        if (!editor.attr('disabled')) {
            editor.parent().removeClass('editing');

            editor.attr('disabled', 'disabled');

            this.captureEditorValue(editor);
            editor.remove();

            //Store update the answer cache
            this.collectAnswers();
        }
    }

    EditApp.prototype.showEditor = function(question) {
        //Blank the form
        this.ui.editorForm[0].reset();
        this.ui.editorAnswersList.empty();

        var self = this;
        //Determine where in the question list the form should go
        if (question) {
            //Position the editor
            question.after(this.ui.editor);

            //Populate the editor
            var qData = new QuestionData(question);
            this.ui.editorSubject.val(qData.subject);
            this.ui.editorText.val(qData.question_text);
            this.ui.editorImage.attr('src', qData.image_src);
            self.setEditorAnswers(qData.answers);

        } else {
            this.ui.questionList.prepend(this.ui.editor);
        }
        
        //Save which question we are editing
        this.currentQuestion = question;
        
        //Expand the editor form
        this.ui.editor.collapse('show');
    };

    var QuestionData = function(question) {
        this.subject = question.find(QUESTION_SUBJECT_SELECTOR).text();
        this.question_text = question.find(QUESTION_TEXT_SELECTOR).text();
        this.image_src = question.find(QUESTION_IMAGE_SELECTOR).attr('src');
        var answerList = question.find(QUESTION_ANSWER_LIST_SELECTOR);
        var answers = this.answers = [];

        answerList.children().each(function(index, listElement) {
            var contents = $(listElement).find(ANSWER_VALUE_SELECTOR).html();
            answers.push($.trim(contents));
        });
    };

    EditApp.prototype.setEditorAnswers = function(answerList) {
        var self = this;
        $.each(answerList, function(index, html) {
            var answer = generateAnswerChoice(html);
            self.ui.editorAnswersList.append(answer);
        });

        this.ui.editorAnswersInput.val(JSON.stringify(answerList));
    };

    EditApp.prototype.addAnswerChoice = function(answerHtml, index) {
        var answer = generateAnswerChoice(answerHtml);
        var answerList = JSON.parse(this.ui.editorAnswersInput.val());

        if (typeof(index) == 'undefined') {
            this.ui.editorAnswersList.append(answer);
            answerList.push($.trim(answerHtml));
        } else {
            //Have to insert it at a position -- todo
            throw "not yet implemented";
        }

        this.ui.editorAnswersInput.val(JSON.stringify(answerList));
    }

    EditApp.prototype.collectAnswers = function(answer) {
        //Just blow away the stored answer value
        var answerList = [];

        this.ui.editorAnswersList.children().each(function(i, listElement) {
            var answerText = $(listElement).find(ANSWER_VALUE_SELECTOR).html();
            answerList.push($.trim(answerText));
        });

        this.ui.editorAnswersInput.val(JSON.stringify(answerList));
    }

    var generateAnswerChoice = function(answerHtml) {
        //Generate an answer icon
        var answer = $('<div>')
            .addClass('value')
            .html($.trim(answerHtml));

        //Editable if nothing but text children
        if (answer.children().size() == 0) {
            answer.addClass('editable');
        }

        return $('<li>').addClass('answer-choice').html(answer);
    };
    
    EditApp.prototype.hideEditor = function() {
        this.ui.editor.collapse('hide');
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