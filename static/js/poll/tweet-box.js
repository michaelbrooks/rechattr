(function() {
    TWEET_LENGTH = 140;
    TWEET_LENGTH_WARNING_CLASS = 'length-warning';
    TWEET_LENGTH_INVALID_CLASS = 'length-invalid';
    
    var hashtag = null;
    var hashtagContains = null;
    var hashtagLength = 0;
    
    var updateTweetLengthMessage = function() {
        var message = this.ui.tweetInput.val().toLowerCase();
        
        var limit = TWEET_LENGTH - hashtagLength;
        var containsHashtag = false;
        //Does the message contain the hashtag?
        if (hashtagContains(message)) {
            limit = TWEET_LENGTH;
            containsHashtag = true;
        }
        this.ui.hashtagBox.toggleClass('in', !containsHashtag);
        
        var remaining = limit - message.length;
        
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
        })
        .on('focus', function(e) {
            self.ui.tweetInputWrapper.addClass('focus');
        })
        .on('blur', function(e) {
            self.ui.tweetInputWrapper.removeClass('focus');
        });
        
        this.ui.newTweetButton.on('click', function(e) {
            self.ui.tweetBox.modal('show');
        });
        
        this.ui.tweetBox.on('shown', function(e) {
            activateTweetBox.call(self, e);
        });
    }
    
    var TweetBox = function() {
        hashtag = this.ui.hashtagBox.data('hashtag');
        hashtagLength = hashtag.length;
        hashtagContains = rechattr.util.twitter.hashtag_contains(hashtag);
        
        attachInteractions.call(this);
        // catchSubmit.call(this);
    }
    
    rechattr.extension.TweetBox = TweetBox;
    return TweetBox;
})();