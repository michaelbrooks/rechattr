(function() {

    var QUESTION_EDITOR_SELECTOR = '.question-editor';
    var PREV_BUTTON_SELECTOR = '.prev-button';
    var NEXT_BUTTON_SELECTOR = '.next-button';

    var SUBJECT_INPUT_SELECTOR = '.question-subject';
    var TEXT_INPUT_SELECTOR = '.question-text';
    var ANSWER_LIST_SELECTOR = '.answer-list';
    var IMAGE_SELECTOR = '.question-image';
    var IMAGE_INPUT_SELECTOR = '.question-image-input';

    var PALETTE_SELECTOR = '.answer-palette';
    var ANSWER_CHOICE_SELECTOR = '.answer-choice';
    var ANSWER_VALUE_SELECTOR = '.value';
    var EDITABLE_VALUE_SELECTOR = '.editable';
    var TRASH_SELECTOR = '.trash-bin';

    var ANSWER_EDITOR_SELECTOR = '.answer-editor';
    var SAVE_BUTTON_SELECTOR = '.question-save';
    var CANCEL_BUTTON_SELECTOR = '.question-cancel';

    var Editor = function() {
        this.initUI();
        this.attachEvents();
    }

    Editor.prototype.initUI = function() {
        this.ui = {};

        var editor = this.ui.el = $(QUESTION_EDITOR_SELECTOR);
        this.ui.paletteNextButton = editor.find(NEXT_BUTTON_SELECTOR);
        this.ui.palettePrevButton = editor.find(PREV_BUTTON_SELECTOR);

        this.ui.subject = editor.find(SUBJECT_INPUT_SELECTOR);
        this.ui.questionText = editor.find(TEXT_INPUT_SELECTOR);
        this.ui.image = editor.find(IMAGE_SELECTOR);
        this.ui.imageInput = editor.find(IMAGE_INPUT_SELECTOR);
        this.ui.palette = editor.find(PALETTE_SELECTOR);
        this.ui.paletteList = this.ui.palette.find('ul');
        this.ui.answersList = editor.find(ANSWER_LIST_SELECTOR);
        this.ui.answerTrash = editor.find(TRASH_SELECTOR);

        this.ui.saveButton = editor.find(SAVE_BUTTON_SELECTOR);
        this.ui.cancelButton = editor.find(CANCEL_BUTTON_SELECTOR);

    }

    Editor.prototype.attachEvents = function() {
        var self = this;

        this.ui.saveButton.on('click', function(e) {
            self.saveAndClose();
        });

        this.ui.cancelButton.on('click', function(e) {
            self.hide();
        });

        this.ui.paletteNextButton.on('click', function(e) {
            self.shiftPalette(1);
        });

        this.ui.palettePrevButton.on('click', function(e) {
            self.shiftPalette(-1);
        });

        this.ui.answersList.on('click', ANSWER_CHOICE_SELECTOR, function(e) {
            if (self.engageAnswerEditor($(this))) {
                e.preventDefault();
                return false;
            } else {
                //The answer editor was not engaged. Uneditable.
            }
        });
        this.ui.answersList.on('blur', ANSWER_EDITOR_SELECTOR, function(e) {
            self.disengageAnswerEditor($(this));
        });
        $(document).on('click', function(e) {
            //Watch global clicks to disengage the editor also
            if ($(e.target).parents(ANSWER_EDITOR_SELECTOR).size() == 0) {
                self.disengageAnswerEditor($(this));
            }
        });


        this.ui.palette.on('click', ANSWER_CHOICE_SELECTOR, function(e) {
            var answerValue = $(this).find(ANSWER_VALUE_SELECTOR)
            self.addAnswerChoice(answerValue.html())
        });

        this.ui.answersList.on('keyup', ANSWER_EDITOR_SELECTOR, function(e) {
            self.captureEditorValue($(this));
        });

        this.ui.answersList.on('keydown', ANSWER_EDITOR_SELECTOR, function(e) {
            //Catch enter presses
            if (e.which == 13) {
                e.preventDefault();

                //This will disengage the editor eventually
                $(this).blur();
                return false;
            }
        });

        //Adapted from:
        //http://dragsort.codeplex.com/discussions/257578
        this.ui.el.on('mousemove', ANSWER_LIST_SELECTOR + ' ' + ANSWER_CHOICE_SELECTOR, function(e) {
            var listItem = $(this);
            var isOverTrash = self.isOverTrash(e, listItem);

            listItem.toggleClass("about-to-delete", isOverTrash);
            self.ui.answerTrash.toggleClass('trash-activate', isOverTrash);
        });

        //Adapted from:
        //http://dragsort.codeplex.com/discussions/257578
        this.ui.el.on('mouseup', ANSWER_LIST_SELECTOR + ' ' + ANSWER_CHOICE_SELECTOR, function(e) {
            var listItem = $(this);
            var isOverTrash = self.isOverTrash(e, listItem);
            if (isOverTrash) {
                listItem.remove();
                self.ui.answersList.dragsort('stop');

                self.ui.answerTrash.removeClass('trash-activate');
                e.preventDefault();
                return false;
            }
        });

        this.ui.answersList.dragsort({
            dragSelector: 'li',
            dragEnd: function() {

            },
            dragBetween: true,
            dragStop: function() {
                //Remove the cursor setting manually, since dragsort is buggy
                $(this).css('cursor', '');
            },
            placeHolderTemplate: '<li class="placeholder"></li>'
        });
    }

    Editor.prototype.isOverTrash = function (e, listItem) {
        //This is adapted from
        //http://dragsort.codeplex.com/discussions/257578
        var bin = this.ui.answerTrash;

        var binPos = bin.offset();
        binPos.right = binPos.left + bin.outerWidth();
        binPos.bottom = binPos.top + bin.outerHeight();

        if (false) {
            var itemPos = listItem.offset();
            itemPos.right = itemPos.left + listItem.outerWidth();
            itemPos.bottom = itemPos.top + listItem.outerHeight();

            var outside = itemPos.right < binPos.left ||
                itemPos.left > binPos.right ||
                itemPos.top > binPos.bottom ||
                itemPos.bottom < binPos.top;

            return !outside;
        } else {
            //Check if the mouse is inside the trash
            var inside = (e.pageX >= binPos.left && e.pageX <= binPos.right &&
                e.pageY >= binPos.top && e.pageY <= binPos.bottom)
            return inside;
        }

    };

    Editor.prototype.shiftPalette = function(by) {
        //Get the palette container width
        var width = this.ui.palette.width();

        //Get the current relative offset
        var offset = this.ui.paletteList.position().left;
        var maxShift = this.ui.paletteList.width() - width;

        var shift = offset - by * width * 0.9;

        //Shift must be between -width and 0
        shift = Math.min(0, Math.max(-maxShift, shift));
        this.ui.paletteList.css('left', shift + 'px');

        if (shift == -maxShift) {
            this.ui.paletteNextButton.attr('disabled', 'disabled');
        } else {
            this.ui.paletteNextButton.removeAttr('disabled');
        }

        if (shift == 0) {
            this.ui.palettePrevButton.attr('disabled', 'disabled');
        } else {
            this.ui.palettePrevButton.removeAttr('disabled');
        }
    }

    Editor.prototype.engageAnswerEditor = function(answer) {
        if (answer.is('.editing')) {
            return;
        }

        if (!answer.is(EDITABLE_VALUE_SELECTOR)) {
            return;
        }

        var answerValue = answer.find(ANSWER_VALUE_SELECTOR);

        //Editable if the value is straight text
        if (answerValue.size()) {
            answer.addClass('editing');

            var value = answerValue.text();
            var input = $('<input>')
                .attr('type', 'text')
                .addClass('answer-editor')
                .val(value);

            answer.append(input);

            input.select();

            return true;
        }
    }

    Editor.prototype.captureEditorValue = function(editor) {
        //Update the answer value from the input element
        var value = editor.val();
        var valueBox = editor.parent().find(ANSWER_VALUE_SELECTOR);
        valueBox.text(value);
    }

    Editor.prototype.disengageAnswerEditor = function(editor) {
        if (!editor.attr('disabled')) {
            editor.parent().removeClass('editing');

            editor.attr('disabled', 'disabled');

            if ($.trim(editor.val()) == '') {
                //Delete items that have been emptied
                editor.parent().remove();
            } else {
                this.captureEditorValue(editor);
                editor.remove();
            }
        }
    }

    Editor.prototype.isShowing = function() {
        return this.ui.el.is('.in');
    }

    Editor.prototype.isEditing = function(question) {
        if (!this.isShowing()) {
            return false;
        }

        if (!this.currentQuestion) {
            return question == this.currentQuestion;
        } else {
            return this.currentQuestion.is(question);
        }
    }


    Editor.prototype.blank = function() {
        //Blank the form
        this.ui.subject.val('');
        this.ui.questionText.val('');
        this.ui.image.attr('src', '');

        this.ui.answersList.empty();

        this.data = new QuestionData();
    }

    Editor.prototype.fill = function(questionItem) {
        var self = this;

        //Populate the editor
        this.data = new QuestionData(questionItem);
        this.ui.subject.val(this.data.get('subject'));
        this.ui.questionText.val(this.data.get('question_text'));
        this.ui.image.attr('src', this.data.get('image_src'));

        $.each(this.data.get('answers'), function(index, html) {
            var answer = generateAnswerChoice(html);
            self.ui.answersList.append(answer);
        });
    }

    Editor.prototype.saveAndClose = function() {
        this.saveAnswers();
        this.data.updateQuestion();
        this.hide();
    }

    Editor.prototype.hide = function() {
        this.ui.el.collapse('hide');
    }

    Editor.prototype.show = function(question) {
        this.currentQuestion = question;

        //Make sure the button scroller is the right size
        var paletteWidth = 0;
        $.each(this.ui.paletteList.children(), function(i, listItem) {
            //true to include margin
            paletteWidth += $(this).outerWidth(true);
        });
        this.ui.paletteList.width(paletteWidth);

        //Expand the editor form
        this.ui.el.collapse('show');
    }

    Editor.prototype.addAnswerChoice = function(answerHtml, index) {
        var answer = generateAnswerChoice(answerHtml);

        if (typeof(index) == 'undefined') {
            this.ui.answersList.append(answer);
        } else {
            //Have to insert it at a position -- todo
            throw "not yet implemented";
        }
    }

    Editor.prototype.saveAnswers = function(answer) {
        this.data.set('subject', this.ui.subject.val());
        this.data.set('question_text', this.ui.questionText.val());
        this.data.set('image_src', this.ui.image.attr('src'));

        var answerList = [];
        this.ui.answersList.children().each(function(i, listElement) {
            var answerText = $(listElement).find(ANSWER_VALUE_SELECTOR).html();
            answerList.push($.trim(answerText));
        });

        this.data.set('answers', answerList);
    }

    Editor.prototype.on = rechattr.util.events.on;
    Editor.prototype.trigger = rechattr.util.events.trigger;

    var generateAnswerChoice = function(answerHtml) {
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

    //An object that collects data from the question display
    var QuestionData = function(question) {
        this.data = {
            subject: "",
            question_text: "",
            image_src: "",
            answers: []
        }
        this.dirty = false;

        if (question) {
            this.question = question;
            this.data.subject = question.find(SUBJECT_INPUT_SELECTOR).text();
            this.data.question_text = question.find(TEXT_INPUT_SELECTOR).text();
            this.data.image_src = question.find(IMAGE_SELECTOR).attr('src');
            var answerList = question.find(ANSWER_LIST_SELECTOR);
            var answers = this.data.answers;

            answerList.children().each(function(index, listElement) {
                var contents = $(listElement).find(ANSWER_VALUE_SELECTOR).html();
                answers.push($.trim(contents));
            });
        }
    };

    QuestionData.prototype.updateQuestion = function() {
        if (!this.question) {
            return;
        }

        this.question.find(SUBJECT_INPUT_SELECTOR).text(this.data.subject);
        this.question.find(TEXT_INPUT_SELECTOR).text(this.data.question_text);
        this.question.find(IMAGE_SELECTOR).attr('src', this.data.image_src);

        var answerList = this.question.find(ANSWER_LIST_SELECTOR);
        answerList.empty();
        $.each(this.data.answers, function(i, value) {
            value = generateAnswerChoice(value);
            answerList.append(value);
        });
    }

    QuestionData.prototype.set = function(member, value) {
        if (member in this.data) {
            if (value !== this.data[member]) {
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

    rechattr.util.Editor = Editor;
    return Editor;
})();