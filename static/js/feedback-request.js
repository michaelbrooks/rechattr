(function() {
    
    var attachInteractions = function() {
        console.log('feedback request');
    }
    
    var FeedbackRequest = function() {
        attachInteractions.call(this);
    }
    
    rechattr.extension.FeedbackRequest = FeedbackRequest;
    return FeedbackRequest;
})();