(function() {
    
    var CHATTER_SELECTOR = '.chatter';
    var FEEDBACK_SELECTOR = '.feedback';
    var CONTAINER_SELECTOR = '.container';
    var CHATTER_POLL_TITLE_SELECTOR = '.chatter .segment-title';
    var FEEDBACK_POLL_TITLE_SELECTOR = '.feedback .segment-title';
    var CHATTER_NOTIFY_SELECTOR = '.chatter-notify';
    var FEEDBACK_NOTIFY_SELECTOR = '.feedback-notify';
    
    function toggleInClass(selection, visible) {
        if (visible) {
            selection.addClass('in');
        } else {
            selection.removeClass('in');
        }
    }
    
    var MobilePoll = function() {
        this.ui = {};
        
        this.ui.container = $(CONTAINER_SELECTOR);
        this.ui.feedback = $(FEEDBACK_SELECTOR);
        this.ui.chatter = $(CHATTER_SELECTOR);
        this.ui.chatterPollTitle = $(CHATTER_POLL_TITLE_SELECTOR);
        this.ui.feedbackPollTitle = $(FEEDBACK_POLL_TITLE_SELECTOR);
        this.ui.chatterNotify = $(CHATTER_NOTIFY_SELECTOR);
        this.ui.feedbackNotify = $(FEEDBACK_NOTIFY_SELECTOR);
        
        
        this.showing = null;
        this.showFeedback();
        
        this.attachInteractions();
        
    }
    
    MobilePoll.prototype.width = function() {
        return this.ui.container.width();
    }
    
    MobilePoll.prototype.titleHeight = function() {
        var titleHeight = this.ui.feedbackPollTitle.height();
        return titleHeight;
    }
    
    MobilePoll.prototype.showChatter = function() {
        if (this.showing != 'chatter') {
            this.showing = 'chatter';
            
            toggleInClass(this.ui.chatter, true);
            toggleInClass(this.ui.feedback, false);
            toggleInClass(this.ui.chatterNotify, false);
            
            var self = this;
            setTimeout(function() {
                toggleInClass(self.ui.feedbackNotify, true);
            }, 2000);

        }
    }
    
    MobilePoll.prototype.showFeedback = function() {
        if (this.showing != 'feedback') {
            this.showing = 'feedback';
            
            toggleInClass(this.ui.feedback, true);
            toggleInClass(this.ui.chatter, false);
            toggleInClass(this.ui.feedbackNotify, false);
            
            var self = this;
            setTimeout(function() {
                toggleInClass(self.ui.chatterNotify, true);
            }, 2000);
        }
    }
    
    MobilePoll.prototype.attachInteractions = function() {
        var self = this;
        
        this.ui.chatter.on('click', function() {
            self.showChatter();
        });
        
        this.ui.feedback.on('click', function() {
            self.showFeedback();
        });
    }
    
    rechattr.classes.MobilePoll = MobilePoll;
    return MobilePoll;
})();