define(function(require) {
    var twitter = require('util/twitter');

    var TWEET_LENGTH = 140;
    var TWEET_LENGTH_WARNING_CLASS = 'length-warning';
    var TWEET_LENGTH_INVALID_CLASS = 'length-invalid';
    
    var hashtag = null;
    var hashtagContains = null;
    var hashtagLength = 0;
    
    var updateTweetLengthMessage = function() {
        var message = this.ui.tweetInput.val().toLowerCase();
        
        var limit = TWEET_LENGTH - hashtagLength - 1; //1 for the space before the hashtag
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
        
        if (remaining < 0 || remaining == limit) {
            this.ui.tweetSubmitButton.attr('disabled', 'disabled');
        } else {
            this.ui.tweetSubmitButton.removeAttr('disabled');
        }
    }
    
    var activateTweetBox = function(e) {
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
        
        this.ui.hashtagBox.on('click', function(e) {
            self.ui.tweetInput.focus();
        });
        
        this.ui.newTweetButton.on('click', function(e) {
            self.ui.tweetBox.modal('show');
        });
        
        this.ui.tweetBox.on('shown', function(e) {
            activateTweetBox.call(self, e);
        });

        this.ui.tweetCancelButton.on('click', function(e) {
            self.ui.tweetBox.modal('hide');
        });
        
        //If there is already input, it must be a failed POST so bring it back up
        if (this.ui.tweetInput.val()) {
            this.ui.tweetBox.modal('show');
            activateTweetBox.call(this);
        }
    }
    
    var TweetBox = function() {
        hashtag = this.ui.hashtagBox.data('hashtag');
        hashtagLength = hashtag.length;
        hashtagContains = twitter.hashtag_contains(hashtag);
        
        attachInteractions.call(this);
        // catchSubmit.call(this);
    }

    return TweetBox;
});