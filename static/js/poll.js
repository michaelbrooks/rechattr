define(function(require) {

    var $ = require('jquery');
    require('vendor/bootstrap');
    var flash = require('util/flash');
    var StreamPanel = require('poll/stream-panel');
    var QuestionBox = require('poll/question-box');
    var TweetBox = require('poll/tweet-box');
    var events = require('util/events');
    //var MobilePanels = require('poll/mobile-panels');

    //Turn off []-appending to posted arrays
    //More: http://forum.jquery.com/topic/jquery-post-1-4-1-is-appending-to-vars-when-posting-from-array-within-array
    $.ajaxSettings.traditional = true;

    var CONTAINER_SELECTOR = '.container';
    var PANEL_SELECTOR = '.panel';
    var PANEL_SCROLL_BOX_SELECTOR = '.panel-content';
    var POLL_TITLE_SELECTOR = '.segment-title';
    var CHATTER_NOTIFY_SELECTOR = '.chatter-notify';
    var FEEDBACK_NOTIFY_SELECTOR = '.feedback-notify';
    var STREAM_LIST_ITEMS_SELECTOR = '.stream-list';
    var STREAM_HEADER_SELECTOR = '.stream-header';
    var STREAM_FOOTER_SELECTOR = '.stream-footer';
    
    var MODAL_BACKDROP_SELECTOR = '.modal-backdrop';
    
    var NEW_TWEET_BUTTON_SELECTOR = '.new-tweet-button';
    var TWEET_MODAL_SELECTOR = '.tweet-modal';
    var TWEET_INPUT_SELECTOR = '.tweet-input';
    var TWEET_INPUT_WRAPPER_SELECTOR = '.tweet-input-wrapper';
    var TWEET_LENGTH_MESSAGE_SELECTOR = '.tweet-length-message';
    var TWEET_SUBMIT_BUTTON_SELECTOR = '.tweet-submit';
    var TWEET_CANCEL_BUTTON_SELECTOR = '.tweet-cancel';
    var TWEET_FORM_SELECTOR = '.tweet-form';
    var HASHTAG_BOX_SELECTOR = '.hashtag-box';

    var QUESTION_MODAL_SELECTOR = '.question-modal';
    var QUESTION_WRAPPER_SELECTOR = '.question-wrapper';


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
        
        flash.initFlash();
        
        StreamPanel.call(this);
        //MobilePanels.call(this);
        TweetBox.call(this);
        QuestionBox.call(this);
        
        this.attachInteractions();
    };
    
    PollApp.prototype.initUI = function() {
        this.ui = {};
        
        this.ui.container = $(CONTAINER_SELECTOR);
        this.ui.panel = $(PANEL_SELECTOR);
        this.ui.panelScroll = this.ui.panel.find(PANEL_SCROLL_BOX_SELECTOR);
        this.ui.pollTitle = $(POLL_TITLE_SELECTOR);
        this.ui.chatterNotify = $(CHATTER_NOTIFY_SELECTOR);
        this.ui.feedbackNotify = $(FEEDBACK_NOTIFY_SELECTOR);
        this.ui.streamList = this.ui.panel.find(STREAM_LIST_ITEMS_SELECTOR);
        this.ui.streamHeader = this.ui.panel.find(STREAM_HEADER_SELECTOR);
        this.ui.streamFooter = this.ui.panel.find(STREAM_FOOTER_SELECTOR);

        //Not used??
        //this.ui.modalBackdrop = $(MODAL_BACKDROP_SELECTOR);
        
        this.ui.newTweetButton = $(NEW_TWEET_BUTTON_SELECTOR);
        
        this.ui.tweetBox = $(TWEET_MODAL_SELECTOR);
        this.ui.tweetInputWrapper = $(TWEET_INPUT_WRAPPER_SELECTOR);
        this.ui.tweetInput = $(TWEET_INPUT_SELECTOR);
        this.ui.hashtagBox = $(HASHTAG_BOX_SELECTOR);
        this.ui.tweetLengthMessage = $(TWEET_LENGTH_MESSAGE_SELECTOR);
        this.ui.tweetSubmitButton = $(TWEET_SUBMIT_BUTTON_SELECTOR);
        this.ui.tweetCancelButton = $(TWEET_CANCEL_BUTTON_SELECTOR);
        this.ui.tweetForm = $(TWEET_FORM_SELECTOR);

        this.ui.questionBox = $(QUESTION_MODAL_SELECTOR);
        this.ui.questionWrapper = this.ui.questionBox.find(QUESTION_WRAPPER_SELECTOR);
    };

    PollApp.prototype.attachInteractions = function() {
//        $('.tooltip-below').tooltip({
//            placement: 'bottom'
//        });
        //removed tooltip because it doesn't work on phones
    };

    events(PollApp);

    window.app = new PollApp();
    return window.app;
});