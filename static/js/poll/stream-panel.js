(function() {
    
    var STREAM_NOTIFY_SELECTOR = '.stream-notify';
    var STREAM_INTERVAL_SECONDS = 20;
    
    var pollId = rechattr.config.poll;
    var lastCheck = rechattr.config.time;
    var interval = null;
    var pendingItems = null;
    var streamUrl = rechattr.config.poll + "/stream";
    
    var startPoll = function() {
        var millis = STREAM_INTERVAL_SECONDS * 1000;
        var self = this;
        interval = setInterval(function() {
            checkStream.call(self);
        }, millis);
    }
    
    var stopPoll = function() {
        if (interval) {
            clearInterval(interval);
        }
    }
    
    var newItems = function(itemCount, html) {
        pendingItems = $(html);
        notifyNewItems.call(this, pendingItems);
    }
    
    var getNotify = function(message) {
        return $('<div>')
        .addClass('stream-notify')
        .text(message);
    }
    
    var notifyNewItems = function(items) {
        console.log("Received", items.size(), "new items");
        var notify = getNotify(items.size() + " new tweets");
        this.ui.streamHeader.html(notify);
        this.ui.streamHeader.addClass('in');
        
        this.trigger('new-items', [items]);
    }
    
    var showPendingItems = function() {
        // Remove any notification
        this.ui.streamHeader.removeClass('in').empty();
        
        if (pendingItems) {
            //Grab pending items for local use
            var pending = pendingItems;
            pendingItems = null;
            
            // Add the items to the stream list
            this.ui.streamList.prepend(pending);
            
            // Do any remaining processing on the items
            processItems.call(this, pending);
            
            
            //Remove the new marking after initial render
            setTimeout(function() {
                pending.removeClass('new-item');
            }, 1);
        }
    }
    
    var checkStream = function() {
        var self = this;
        
        var since = lastCheck;
        var data = {
            since: since
        }
        
        var request = $.get(streamUrl, data, 'json');
        
        request.done(function(response) {
            if (typeof response === 'string') {
                response = JSON.parse(response)
            }
            
            lastCheck = response.time;
            if (response.items > 0) {
                self._callback(response.items, response.html);
            }
        });
    }
    
    var attachInteractions = function() {
        var self = this;
        var showPendingItemsProxy = function() {
            showPendingItems.call(self);
        };
    
        this.ui.streamHeader.delegate(STREAM_NOTIFY_SELECTOR, 'click', showPendingItemsProxy);
    }
    
    var processItems = function(selection) {
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
    
    var attachEventHandlers = function() {
        this.on('show-pending-items', showPendingItems, this)
    }
    
    var StreamPanel = function() {
        //FOR TESTING//
        var tweets = this.ui.streamList.children().slice(0,5);
        tweets.remove();
        tweets.addClass('new-item');
        var self = this;
        setTimeout(function() {
            newItems.call(self, tweets.size(), tweets);
        }, 5000);
        //FOR TESTING//
    
        attachInteractions.call(this);
        attachEventHandlers.call(this);
        startPoll.call(this);
        
        //Process initial stream items
        processItems.call(this, this.ui.streamList.children());
    };
    
    rechattr.extension.StreamPanel = StreamPanel;
    return StreamPanel;
})();