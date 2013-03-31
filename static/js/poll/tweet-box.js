(function() {
    TWEET_LENGTH = 140;
    TWEET_LENGTH_WARNING_CLASS = 'length-warning';
    TWEET_LENGTH_INVALID_CLASS = 'length-invalid';
    
    var updateTweetLengthMessage = function() {
        var message = this.ui.tweetInput.val();
        var remaining = TWEET_LENGTH - message.length;
        
        this.ui.tweetLengthMessage.text(remaining);
        
        this.ui.tweetLengthMessage.toggleClass(TWEET_LENGTH_WARNING_CLASS, remaining < 10);
        this.ui.tweetLengthMessage.toggleClass(TWEET_LENGTH_INVALID_CLASS, remaining < 0);
        
        if (remaining < 0 || remaining == TWEET_LENGTH) {
            this.ui.tweetSubmitButton.attr('disabled', 'disabled');
        } else {
            this.ui.tweetSubmitButton.removeAttr('disabled');
        }
    }
    
    var activateTweetBox = function(e) {
        // var width = this.ui.tweetForm.width();
        // this.ui.tweetInput.outerWidth(width);
        
        this.ui.tweetInput.focus();
        
        updateTweetLengthMessage.call(this);
    }
    
    var attachInteractions = function() {
        var self = this;
        this.ui.tweetInput.on('keydown keyup', function(e) {
            updateTweetLengthMessage.call(self, e);
        });
        
        this.ui.newTweetButton.on('click', function(e) {
            self.ui.tweetBox.modal('show');
        });
        
        this.ui.tweetBox.on('shown', function(e) {
            activateTweetBox.call(self, e);
        });
        
        this.ui.newTweetButton.tooltip({
            placement: 'bottom'
        });
    }
    
    var TweetBox = function() {
        attachInteractions.call(this);
        // catchSubmit.call(this);
    }
    
    rechattr.extension.TweetBox = TweetBox;
    return TweetBox;
})();