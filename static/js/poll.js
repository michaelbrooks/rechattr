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
    var STREAM_NOTIFY_SELECTOR = '.stream-notify';
    
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
        
        var tweets = this.ui.streamList.children().slice(0,5);
        tweets.remove();
        tweets.addClass('new-item');
        
        var self = this;
        setTimeout(function() {
            self.newItems(tweets.size(), tweets);
        }, 5000);
        
        this.initStream();
        
        rechattr.extension.MobilePanels.call(this);
        
        this.attachInteractions();
    };
    
    PollApp.prototype.processItems = function(selection) {
        selection.each(function(index, element) {
            var $this = $(this);
            
            var itemType = $this.data('stream-item-type');
            switch (itemType) {
                case 'tweet':
                    rechattr.extension.Tweet($this);
                    break;
                case 'request':
                    rechattr.extension.FeedbackRequest($this);
                    break;
            }
        });
    }
    
    PollApp.prototype.initStream = function() {
        var self = this;
        
        this.stream = new rechattr.util.Stream({
            poll: rechattr.config.poll,
            time: rechattr.config.time
        });
        
        this.stream.done(function(itemCount, html) {
            self.newItems(itemCount, html);
        })
        .start();
        
        this.processItems(this.ui.streamList.children());
    }
    
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
    
    PollApp.prototype.attachInteractions = function() {
        var self = this;
        var showPendingItemsProxy = function() {
            self.showPendingItems();
        };
    
        this.ui.streamHeader.delegate(STREAM_NOTIFY_SELECTOR, 'click', showPendingItemsProxy);
    }
    
    PollApp.prototype.newItems = function(itemCount, html) {
        this._pendingItems = $(html);
        this.notifyNewItems(this._pendingItems);
    }
    
    PollApp.prototype.notifyNewItems = function(items) {
        console.log("Received", items.size(), "new items");
        debugger;
        var notify = getNotify(items.size() + " new tweets");
        this.ui.streamHeader.html(notify);
        this.ui.streamHeader.addClass('in');
    }
    
    var getNotify = function(message) {
        return $('<div>')
        .addClass('stream-notify')
        .text(message);
    }
    
    PollApp.prototype.showPendingItems = function() {
        // Remove any notification
        this.ui.streamHeader.removeClass('in').empty();
        
        if (this._pendingItems) {
            var pending = this._pendingItems;
            this._pendingItems = null;
            
            // Add the items to the stream list
            this.ui.streamList.prepend(pending);
            
            // Do any remaining processing on the items
            this.processItems(pending);
            
            
            //Remove the new marking after initial render
            var self = this;
            setTimeout(function() {
                pending.removeClass('new-item');
            }, 1);
        }
    }
    
    rechattr.classes.PollApp = PollApp;
    return PollApp;
})();