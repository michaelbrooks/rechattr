(function() {
    var CHATTER_SELECTOR = '.chatter';
    var FEEDBACK_SELECTOR = '.feedback';
    var CONTAINER_SELECTOR = '.container';
    var CHATTER_POLL_TITLE_SELECTOR = '.chatter .segment-title';
    var FEEDBACK_POLL_TITLE_SELECTOR = '.feedback .segment-title';
    var CHATTER_NOTIFY_SELECTOR = '.chatter-notify';
    var FEEDBACK_NOTIFY_SELECTOR = '.feedback-notify';
    var STREAM_LIST_ITEMS_SELECTOR = '.stream-list';
    var STREAM_HEADER_SELECTOR = '.stream-header';
    
    // var QUESTION_CLASS = 'answer-list';
    // var BUTTON_CLASS = 'answer-btn';
    
    // var BUTTON_ACTIVE_CLASS = 'active';
    // var QUESTION_ANSWERED_CLASS = 'selection-made';
    
    // var QUESTION_NAME_DATA = 'question-name';
    // var ANSWER_VALUE_DATA = 'option'
    
    // var SUBMIT_MESSAGE = 'Sending feedback...';
    
    // var TWEET_LIST_CONTENT_CLASS = 'tweet-list-content';
    
    var PollApp = function() {
        this.initUI();
        
        this.$ = $(this);
        
        rechattr.extension.StreamPanel.call(this);
        rechattr.extension.MobilePanels.call(this);
        
        this.attachInteractions();
    };
    
    PollApp.prototype.initUI = function() {
        this.ui = {};
        
        this.ui.container = $(CONTAINER_SELECTOR);
        this.ui.feedback = $(FEEDBACK_SELECTOR);
        this.ui.chatter = $(CHATTER_SELECTOR);
        this.ui.chatterPollTitle = $(CHATTER_POLL_TITLE_SELECTOR);
        this.ui.feedbackPollTitle = $(FEEDBACK_POLL_TITLE_SELECTOR);
        this.ui.chatterNotify = $(CHATTER_NOTIFY_SELECTOR);
        this.ui.feedbackNotify = $(FEEDBACK_NOTIFY_SELECTOR);
        this.ui.streamList = $(STREAM_LIST_ITEMS_SELECTOR);
        this.ui.streamHeader = $(STREAM_HEADER_SELECTOR);
    }
    
    PollApp.prototype.on = function(event, fun, context) {
        if (context) {
            return this.$.on(event, function() {
                fun.apply(context, arguments);
            });
        } else {
            return this.$.on.apply(this.$, arguments);
        }
    }
    
    PollApp.prototype.trigger = function() {
        return this.$.trigger.apply(this.$, arguments);
    }
    
    PollApp.prototype.attachInteractions = function() {
        
    }
    
    rechattr.classes.PollApp = PollApp;
    return PollApp;
})();