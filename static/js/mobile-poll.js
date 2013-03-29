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
    
    function toggleMovingClass(selection, visible) {
        if (visible) {
            selection.addClass('moving');
        } else {
            selection.removeClass('moving');
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
        
        var width = this.width();
        var offset = 0;
        var margin = this.titleHeight();
        var leftBoundary = 0;
        var rightBoundary = width;
        var squeezeRoom = 3;
        
        var showChatter = function() {
            self.showChatter();
        }
        var showFeedback = function() {
            self.showFeedback();
        }
        var moveStarted = function(e) {
            // If the movestart heads off in a upwards or downwards
            // direction, prevent it so that the browser scrolls normally.
            if ((e.distX > e.distY && e.distX < -e.distY) ||
                (e.distX < e.distY && e.distX > -e.distY)) {
                e.preventDefault();
                return;
            }

            // If feedback panel is active is the target, don't continue
            if (self.showing == 'feedback' &&
                (self.ui.feedback[0] == e.target || self.ui.feedback.find(e.target).size() > 0)) {
                e.preventDefault();
                return;
            }
            
            // To allow the slide to keep step with the finger,
            // temporarily disable transitions.
            self.ui.chatter.addClass('no-transition');
            
            //Save this value for later
            width = self.width();
            margin = self.titleHeight();
            leftBoundary = 100 * 2 * margin / width - squeezeRoom;
            rightBoundary = 100 + squeezeRoom;
            if (self.showing == 'chatter') {
                offset = 2 * margin - e.startX;
            } else {
                offset = width - e.startX;
            }
        }
        
        var updatePosition = function(e) {
            // percent moved horizontally
            var position = e.pageX + offset;
            var left = 100 * position / width;
            // var margin = 64;
            // var percentMargin = 100 * margin / width;
            // var range = width - margin;
            
            left = Math.max(leftBoundary, Math.min(rightBoundary, left));
            
            // Move chatter with the finger
            self.ui.chatter.css('left', left + '%');
            
            var physicalLeft = position - margin;
            
            toggleMovingClass(self.ui.chatter, physicalLeft < width - 2 * margin);
            toggleMovingClass(self.ui.feedback, physicalLeft < 2 * margin);
        }
        
        var moveEnded = function(e) {
            self.ui.chatter.removeClass('no-transition');
            
            self.ui.chatter.css('left', '');
            
            toggleMovingClass(self.ui.chatter, false);
            toggleMovingClass(self.ui.feedback, false);
        }
        
        this.ui.chatter.on('click', showChatter)
        .on('swipeleft', showChatter)
        .on('swiperight', showFeedback)
        .on('movestart', moveStarted)
        .on('move', updatePosition)
        .on('moveend', moveEnded);
        
        this.ui.feedback.on('click', showFeedback)
        .on('swiperight', showFeedback)
        .on('movestart', moveStarted)
        .on('move', updatePosition)
        .on('moveend', moveEnded);
        
    }
    
    rechattr.classes.MobilePoll = MobilePoll;
    return MobilePoll;
})();