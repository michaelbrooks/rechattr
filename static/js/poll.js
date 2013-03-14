(function() {
    var QUESTION_CLASS = 'answer-list';
    var BUTTON_CLASS = 'answer-btn';
    
    var BUTTON_ACTIVE_CLASS = 'active';
    var QUESTION_ANSWERED_CLASS = 'selection-made';
    
    var QUESTION_NAME_DATA = 'question-name';
    var ANSWER_VALUE_DATA = 'option'
    
    var SUBMIT_MESSAGE = 'Sending feedback...';
    
    var PollApp = function() {
        this.questions = this.getQuestions();
        
        var firstQuestion = this.questions.first();
        var lastQuestion = this.questions.last();
        
        var self = this;
        
        //If there are two questions, show the next one on click
        if (this.questions.length > 1) {
            this.getButtonsFor(firstQuestion).on('click', function() {
                self.showHidden(lastQuestion);
                
                var selectedButton = $(this);
                self.updateAnswerSelection(firstQuestion, selectedButton);
                self.updateAnswerSelection(lastQuestion, null);
            });
        }
        
        //The last question submits the form
        this.getButtonsFor(lastQuestion).on('click', function() {
            var selectedButton = $(this);
            self.updateAnswerSelection(lastQuestion, selectedButton);
            
            self.pollComplete();
        });
    };
    
    PollApp.prototype.updateAnswerSelection = function(question, selected) {
        //Reset current active setting
        var buttons = this.getButtonsFor(question);
        buttons.removeClass(BUTTON_ACTIVE_CLASS);
        question.removeClass(QUESTION_ANSWERED_CLASS);
        
        if (selected) {
            question.addClass(QUESTION_ANSWERED_CLASS);
            selected.addClass(BUTTON_ACTIVE_CLASS);
        }
    }
    
    PollApp.prototype.showHidden = function(selection) {
        selection.show();
        setTimeout(function() {
            selection.addClass('in');
        }, 1);
    }
    
    PollApp.prototype.pollComplete = function() {
        var self = this;
        rechattr.util.showOverlay(SUBMIT_MESSAGE);
        
        var response = {};
        this.questions.each(function(index, element) {
            var question = $(element)
            var key = question.data(QUESTION_NAME_DATA)
            
            var buttons = self.getButtonsFor(question);
            var value = buttons.filter('.' + BUTTON_ACTIVE_CLASS).data(ANSWER_VALUE_DATA)
            
            response[key] = value;
        });
        
        this.submitResponse(response);
    }
    
    PollApp.prototype.getQuestions = function() {
        return $('.' + QUESTION_CLASS);
    }
    
    PollApp.prototype.getButtonsFor = function(question) {
        return question.find('.' + BUTTON_CLASS);
    }
    
    PollApp.prototype.submitResponse = function(response) {
        var form = $('form');
        $.each(response, function(key, value) {
            $('<input>', {
                type: 'hidden',
                name: key,
                value: value
            })
            .appendTo(form);
        });
        form.submit();
    }
    
    rechattr.classes.PollApp = PollApp;
    return PollApp;
})();