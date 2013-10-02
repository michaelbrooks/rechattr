define(function(require) {

    require('vendor/jquery.event.move');
    require('vendor/jquery.event.swipe');

    var IN_CLASS = 'in';
    var OUT_CLASS = 'out';
    var ALMOST_IN_CLASS = 'almost-in';
    var ALMOST_OUT_CLASS = 'almost-out';

    var getWidth = function() {
        return this.ui.container.width();
    };
    
    var getTitleHeight = function() {
        return 32;
        //this.ui.feedbackPollTitle.height();
    };
    
    var updateInOut = function() {
        if (showing === 'feedback') {
            this.ui.feedback.toggleClass(IN_CLASS, true);
            this.ui.feedback.toggleClass(OUT_CLASS, false);
            this.ui.chatter.toggleClass(IN_CLASS, false);
            this.ui.chatter.toggleClass(OUT_CLASS, true);
        } else {
            this.ui.chatter.toggleClass(IN_CLASS, true);
            this.ui.chatter.toggleClass(OUT_CLASS, false);
            this.ui.feedback.toggleClass(IN_CLASS, false);
            this.ui.feedback.toggleClass(OUT_CLASS, true);
        }
    };
    
    var showChatter = function() {
        if (showing !== 'chatter') {
            showing = 'chatter';
            
            updateInOut.call(this);
            
            this.ui.chatterNotify.toggleClass(IN_CLASS, false);
            
            this.trigger('show-pending-items');
        }
    };
    
    var showFeedback = function() {
        if (showing !== 'feedback') {
            showing = 'feedback';
            
            updateInOut.call(this);
            
            this.ui.feedbackNotify.toggleClass(IN_CLASS, false);
        }
    };
    
    var attachInteractions = function() {
        var self = this;
        
        var width = getWidth.call(this);
        var offset = 0;
        var margin = getTitleHeight.call(this);
        var leftBoundary = 0;
        var rightBoundary = width;
        var squeezeRoom = 3;
        
        var moveStarted = function(e) {
            // If the movestart heads off in a upwards or downwards
            // direction, prevent it so that the browser scrolls normally.
            if ((e.distX > e.distY && e.distX < -e.distY) ||
                (e.distX < e.distY && e.distX > -e.distY)) {

                e.preventDefault();
                return;
            }

            // If feedback panel is active and is the target, don't continue
            if (showing === 'feedback' &&
                (self.ui.feedback[0] === e.target || self.ui.feedback.find(e.target).size() > 0)) {
                e.preventDefault();
                return;
            }
            
            // To allow the slide to keep step with the finger,
            // temporarily disable transitions.
            self.ui.chatter.addClass('no-transition');
            
            //Disable the main state classes
            self.ui.feedback.toggleClass(IN_CLASS + " " + OUT_CLASS, false);
            self.ui.chatter.toggleClass(IN_CLASS + " " + OUT_CLASS, false);
            
            //Prepare variables for horizontal sliding
            width = getWidth.call(self);
            margin = getTitleHeight.call(self);
            leftBoundary = 100 * 2 * margin / width - squeezeRoom;
            rightBoundary = 100 + squeezeRoom;
            if (showing === 'chatter') {
                self.ui.feedback.toggleClass(ALMOST_IN_CLASS, false);
                self.ui.feedback.toggleClass(ALMOST_OUT_CLASS, true);
                
                self.ui.chatter.toggleClass(ALMOST_IN_CLASS, true);
                self.ui.chatter.toggleClass(ALMOST_OUT_CLASS, false);
                
                offset = 2 * margin - e.startX;
            } else {
                self.ui.feedback.toggleClass(ALMOST_IN_CLASS, true);
                self.ui.feedback.toggleClass(ALMOST_OUT_CLASS, false);
                
                self.ui.chatter.toggleClass(ALMOST_IN_CLASS, false);
                self.ui.chatter.toggleClass(ALMOST_OUT_CLASS, true);
                
                offset = width - e.startX;
            }
            
            updatePosition.call(this, e);
        };
        
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
            
            self.ui.chatter.toggleClass(ALMOST_OUT_CLASS, physicalLeft >= width - 2 * margin);
            self.ui.chatter.toggleClass(ALMOST_IN_CLASS, physicalLeft < width - 2 * margin);
            
            self.ui.feedback.toggleClass(ALMOST_IN_CLASS, physicalLeft >= 2 * margin);
            self.ui.feedback.toggleClass(ALMOST_OUT_CLASS, physicalLeft < 2 * margin);
        };
        
        var moveEnded = function(e) {
            self.ui.chatter.removeClass('no-transition');
            
            self.ui.chatter.css('left', '');
            
            self.ui.feedback.toggleClass(ALMOST_IN_CLASS + " " + ALMOST_OUT_CLASS, false);
            self.ui.chatter.toggleClass(ALMOST_IN_CLASS + " " + ALMOST_OUT_CLASS, false);
            
            updateInOut.call(self);
        };
        
        
        var showChatterProxy = function() {
            showChatter.call(self);
        };
        
        var showFeedbackProxy = function() {
            showFeedback.call(self);
        };
        
        var onSwipeDown = function() {
            if (showing = 'chatter') {
                this.trigger('show-pending-items');
            }
        };
        
        this.ui.chatter.on('click', showChatterProxy)
        .on('swipeleft', showChatterProxy)
        .on('swiperight', showFeedbackProxy)
        .on('movestart', moveStarted)
        .on('move', updatePosition)
        .on('moveend', moveEnded);
        
        this.ui.feedback.on('click', showFeedbackProxy)
        .on('swiperight', showFeedbackProxy)
        .on('movestart', moveStarted)
        .on('move', updatePosition)
        .on('moveend', moveEnded);
        
    };
    
    var onNewItems = function(items) {
        if (showing === 'feedback') {
            this.ui.chatterNotify.toggleClass(IN_CLASS, true);
        }
    };
    
    var attachNotificationHandler = function() {
        this.on('new-items', onNewItems, this);
    };
    
    var showing = null;
    var MobilePanels = function() {
        showFeedback.call(this);
        attachInteractions.call(this);
        attachNotificationHandler.call(this);
    };

    return MobilePanels;
});