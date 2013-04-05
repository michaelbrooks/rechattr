(function() {

    var TIME_FORMAT = 'h:mma';
    var DATE_FORMAT = 'M/DD/YYYY';
    var DATE_PICKER_FORMAT = 'm/dd/yyyy'
    
    var DEFAULT_DURATION = 60*60; //1 hour in seconds
    var TIMELINE_WRAPPER_SELECTOR = '.timeline-wrapper';
    var QUESTION_LIST_SELECTOR = '.question-list';
    
    var EditApp = function() {
        var self = this;
        
        this.initUI();
        
        this.timeline = new rechattr.util.Timeline(this.ui.timelineWrapper);
        
        this.attachTimelineEvents();
    }
    
    EditApp.prototype.initUI = function() {
        this.ui = {};
        
        this.ui.timelineWrapper = $(TIMELINE_WRAPPER_SELECTOR);
        
        this.ui.questionList = $(QUESTION_LIST_SELECTOR);
    }
    
    EditApp.prototype.attachTimelineEvents = function() {
        var self = this;
        $(this.timeline).on('new-bead', function(e, bead) {
            
            var question = new Question();
            self.ui.questionList.append(question.render());
            
            bead.data('question', question);
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

    var Question = function() {
        this.message = 'asdf';
        
        this.$el = $('<div>').addClass('question');
    }
    
    Question.prototype.render = function() {
        this.$el.text(this.message);
        
        return this.$el;
    }
    
    rechattr.classes.EditApp = EditApp;
    return EditApp;
})()