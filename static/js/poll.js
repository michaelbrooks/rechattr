define(function(require) {

    var $ = require('jquery');
    require('vendor/bootstrap');
    var flash = require('util/flash');
    var Question = require('poll/question');
    var StreamPanel = require('poll/stream-panel');
    var TweetBox = require('poll/tweet-box');
    var events = require('util/events');
    //var MobilePanels = require('poll/mobile-panels');

    //Turn off []-appending to posted arrays
    //More: http://forum.jquery.com/topic/jquery-post-1-4-1-is-appending-to-vars-when-posting-from-array-within-array
    $.ajaxSettings.traditional = true;

    var STREAM_LIST_ITEMS_SELECTOR = '.stream-list';
    var STREAM_HEADER_SELECTOR = '.stream-header';
    var STREAM_FOOTER_SELECTOR = '.stream-footer';

    var NEW_TWEET_BUTTON_SELECTOR = '.new-tweet-button';
    var TWEET_MODAL_SELECTOR = '.tweet-modal';
    var TWEET_INPUT_SELECTOR = '.tweet-input';
    var TWEET_INPUT_WRAPPER_SELECTOR = '.tweet-input-wrapper';
    var TWEET_LENGTH_MESSAGE_SELECTOR = '.tweet-length-message';
    var TWEET_SUBMIT_BUTTON_SELECTOR = '.tweet-submit';
    var TWEET_CANCEL_BUTTON_SELECTOR = '.tweet-cancel';
    var TWEET_FORM_SELECTOR = '.tweet-form';
    var HASHTAG_BOX_SELECTOR = '.hashtag-box';

    var QUESTION_SELECTOR = '.question';

    var PollApp = function() {
        this.initUI();
        
        this.$ = $(this);
        
        flash.initFlash();
        
        StreamPanel.call(this);
        TweetBox.call(this);
        
        this.attachInteractions();
    };
    
    PollApp.prototype.initUI = function() {
        this.ui = {};

        this.ui.streamList = $(STREAM_LIST_ITEMS_SELECTOR);
        this.ui.streamHeader = $(STREAM_HEADER_SELECTOR);
        this.ui.streamFooter = $(STREAM_FOOTER_SELECTOR);

        this.ui.newTweetButton = $(NEW_TWEET_BUTTON_SELECTOR);
        
        this.ui.tweetBox = $(TWEET_MODAL_SELECTOR);
        this.ui.tweetInputWrapper = $(TWEET_INPUT_WRAPPER_SELECTOR);
        this.ui.tweetInput = $(TWEET_INPUT_SELECTOR);
        this.ui.hashtagBox = $(HASHTAG_BOX_SELECTOR);
        this.ui.tweetLengthMessage = $(TWEET_LENGTH_MESSAGE_SELECTOR);
        this.ui.tweetSubmitButton = $(TWEET_SUBMIT_BUTTON_SELECTOR);
        this.ui.tweetCancelButton = $(TWEET_CANCEL_BUTTON_SELECTOR);
        this.ui.tweetForm = $(TWEET_FORM_SELECTOR);
    };

    PollApp.prototype.attachInteractions = function() {

    };

    events(PollApp);

    window.app = new PollApp();
    return window.app;
});