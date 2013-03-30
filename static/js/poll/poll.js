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
    
    var MODAL_BACKDROP_SELECTOR = '.modal-backdrop';
    
    var NEW_TWEET_BUTTON_SELECTOR = '.new-tweet-button';
    var TWEET_MODAL_SELECTOR = '.tweet-modal';
    var TWEET_INPUT_SELECTOR = '.tweet-input';
    var TWEET_LENGTH_MESSAGE_SELECTOR = '.tweet-length-message';
    var TWEET_SUBMIT_BUTTON_SELECTOR = '.tweet-submit';
    var TWEET_FORM_SELECTOR = '.tweet-form';
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
        
        rechattr.util.initFlash();
        
        rechattr.extension.StreamPanel.call(this);
        rechattr.extension.MobilePanels.call(this);
        rechattr.extension.TweetBox.call(this);
        
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
        
        this.ui.modalBackdrop = $(MODAL_BACKDROP_SELECTOR);
        
        this.ui.newTweetButton = $(NEW_TWEET_BUTTON_SELECTOR);
        this.ui.tweetBox = $(TWEET_MODAL_SELECTOR);
        this.ui.tweetInput = $(TWEET_INPUT_SELECTOR);
        this.ui.tweetLengthMessage = $(TWEET_LENGTH_MESSAGE_SELECTOR);
        this.ui.tweetSubmitButton = $(TWEET_SUBMIT_BUTTON_SELECTOR);
        this.ui.tweetForm = $(TWEET_FORM_SELECTOR);
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