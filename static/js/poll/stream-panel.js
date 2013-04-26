(function () {

    var STREAM_NOTIFY_SELECTOR = '.stream-notify';
    var STREAM_INTERVAL_SECONDS = 20;
    var TIME_UPDATE_INTERVAL_SECONDS = 60;
    var ITEM_CREATED_AT_SELECTOR = '.created-at';

    var pollId = rechattr.config.poll;
    var mostRecentItemTime = rechattr.config.time;
    var oldestItemTime = rechattr.config.end_of_stream;
    var streamInterval = null;
    var timeUpdateInterval = null;
    var pendingItems = null;
    var noMoreItems = null;
    var loadingMoreItems = null;
    var streamUrl = rechattr.config.poll + "/stream";

    var startPoll = function () {
        var self = this;
        streamInterval = setInterval(function () {
            checkStream.call(self);
        }, STREAM_INTERVAL_SECONDS * 1000);

        timeUpdateInterval = setInterval(function () {
            updateStreamTimes.call(self);
        }, TIME_UPDATE_INTERVAL_SECONDS * 1000);
    }

    var stopPoll = function () {
        if (streamInterval) {
            clearInterval(streamInterval);
        }
        if (timeUpdateInterval) {
            clearInterval(timeUpdateInterval);
        }
    }

    var newItems = function (itemCount, html) {
        pendingItems = $(html);
        notifyNewItems.call(this, pendingItems);
    }

    var getNotify = function (message) {
        return $('<div>')
            .addClass('stream-notify')
            .text(message);
    }

    var notifyNewItems = function (items) {
        console.log("Received", items.size(), "new items");
        var notify = getNotify(items.size() + " new tweets");
        this.ui.streamHeader.html(notify);
        this.ui.streamHeader.addClass('in');

        this.trigger('new-items', [items]);
    }

    var showPendingItems = function () {
        // Remove any notification
        this.ui.streamHeader.removeClass('in').empty();

        if (pendingItems) {
            //Grab pending items for local use
            var pending = pendingItems;
            pendingItems = null;

            // Add the items to the stream list
            this.ui.streamList.prepend(pending);

            //Find the first question and pull it to the top
            var question = this.ui.streamList.find('.question').first();
            if (question.length) {
                this.ui.streamList.prepend(question);
            }

            // Do any remaining processing on the items
            processItems.call(this, pending);


            //Remove the new marking after initial render
            setTimeout(function () {
                pending.removeClass('new-item');
            }, 1);
        }
    }

    var checkStream = function () {
        var self = this;

        var data = {
            since: mostRecentItemTime
        }

        var request = $.get(streamUrl, data, 'json');

        request.done(function (response) {
            if (typeof response === 'string') {
                response = JSON.parse(response)
            }

            if (response.items > 0) {
                //only update the response time if there were items returned because otherwise it is undefined
                mostRecentItemTime = response.time_to;
                newItems.call(self, response.items, response.html)
            }
        });
    }

    var showLoadingMore = function () {
        console.log("Loading more items...");
        this.ui.streamFooter.html(getNotify('Loading...'));
        this.ui.streamFooter.addClass('in');
    }

    var checkForMore = function() {
        if (noMoreItems || loadingMoreItems) {
            return;
        }
        loadingMoreItems = true;

        showLoadingMore.apply(this);

        //Try and load some more stuff below
        var data = {
            before: oldestItemTime
        }

        var request = $.get(streamUrl, data, 'json');

        var self = this;
        request.done(function (response) {
            if (typeof response === 'string') {
                response = JSON.parse(response)
            }

            if (response.items > 0) {
                //only update the time if there were items returned because otherwise it is undefined
                oldestItemTime = response.time_from;
                addItemsAtBottom.call(self, $(response.html))
            } else {
                console.log('No more items');
                noMoreItems = true;
            }

            self.ui.streamFooter.removeClass('in').empty();

            loadingMoreItems = false;
        });

        request.error(function(xhr) {
            console.log("Error loading items", xhr);
            self.ui.streamFooter.html(getNotify('Sorry, please try later.'));
            self.ui.streamFooter.removeClass('in').empty();

            loadingMoreItems = false;
        });
    }

    var addItemsAtBottom = function(items) {
        console.log("Loaded " + items.length + " old items");

        // Add the items to the stream list
        this.ui.streamList.append(items);

        // Do any remaining processing on the items
        processItems.call(this, items);

        //Remove the new marking after initial render
        setTimeout(function () {
            items.removeClass('new-item');
        }, 1);
    }

    var updateStreamTimes = function () {
        this.ui.streamList.find(ITEM_CREATED_AT_SELECTOR).each(function () {
            var $this = $(this);
            var created = $this.data('created');
            if (!created) {
                return;
            }
            created = rechattr.util.time_ago(created);
            $this.text(created);
        });
    }

    var attachInteractions = function () {
        var self = this;
        var showPendingItemsProxy = function () {
            showPendingItems.call(self);
        };

        this.ui.streamHeader.delegate(STREAM_NOTIFY_SELECTOR, 'click', showPendingItemsProxy);
    }

    var processItems = function (selection) {
        selection.each(function (index, element) {
            var $this = $(this);

            //Process the created date if it exists
            var timeElement = $this.find(ITEM_CREATED_AT_SELECTOR)
            var created = timeElement.data('created');
            if (created) {
                timeElement.data('created', new Date(created * 1000));
            }

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

    var attachEventHandlers = function () {
        this.on('show-pending-items', showPendingItems, this);

        var self = this;
        this.ui.panelScroll.on('scroll', function() {
            if (loadingMoreItems) {
                return;
            }

            var bottom = 0;
            self.ui.panelScroll.children().each(function(){
                bottom += $(this).outerHeight();
            });

            var scrollBottom = self.ui.panelScroll.scrollTop() + self.ui.panelScroll.height();

            if (scrollBottom == bottom) {
                checkForMore.apply(self);
            }
        });
    }

    var StreamPanel = function () {
        //FOR TESTING//
        // var tweets = this.ui.streamList.children().slice(0,5);
        // tweets.remove();
        // tweets.addClass('new-item');
        // var self = this;
        // setTimeout(function() {
        // newItems.call(self, tweets.size(), tweets);
        // }, 5000);
        //FOR TESTING//

        attachInteractions.call(this);
        attachEventHandlers.call(this);
        startPoll.call(this);

        //move the most recent question to the top
        var question = this.ui.streamList.find('.question').first()
        if (question.length) {
            this.ui.streamList.prepend(question);
        }
        //Process initial stream items
        processItems.call(this, this.ui.streamList.children());
    };

    rechattr.extension.StreamPanel = StreamPanel;
    return StreamPanel;
})();