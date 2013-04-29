define(function (require) {

    var $ = require('jquery');
    var config = require('config');
    var dtutils = require('util/dtutils');

    var STREAM_NOTIFY_SELECTOR = '.stream-notify';
    var STREAM_INTERVAL_SECONDS = 4;
    var TIME_UPDATE_INTERVAL_SECONDS = 60;
    var ITEM_CREATED_AT_SELECTOR = '.created-at';

    var pollId = config.poll;
    var mostRecentItemTime = config.time;
    var oldestItemTime = config.end_of_stream;

    var streamInterval = null;
    var timeUpdateInterval = null;
    var pendingItems = null;
    var noMoreItems = null;
    var itemHash = {}; //for storing maps from ids to elements
    var loadingMoreItems = null;
    var streamUrl = config.poll + "/stream";

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
        console.log("Received", itemCount, "new items");

        //Filter out all text nodes
        var newItems = $(html).filter(function(i, el) {
            return el.nodeType != 3;
        });

        if (pendingItems) {
            pendingItems = newItems.add(pendingItems);
        } else {
            pendingItems = newItems;
        }

        notifyNewItems.call(this, pendingItems);
    }

    var getNotify = function (message) {
        return $('<div>')
            .addClass('stream-notify')
            .text(message);
    }

    var notifyNewItems = function (items) {
        var questions = items.filter('.question').size();
        var tweets = items.filter('.tweet').size();
        var message = '';
        if (tweets > 0) message = tweets + " new tweets"
        if (questions > 0) {
            if (tweets > 0) {
                message += " & "
            }
            message += questions + " new questions"
        }

        var notify = getNotify(message);
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

            // Remove any duplicates
            var self = this;
            pending.each(function(i, el) {
                var id = $(el).data('id');
                if (id in itemHash) {
                    itemHash[id].remove();
                }
            });

            // Add the items to the stream list
            this.ui.streamList.prepend(pending);

//            //Find the first question and pull it to the top
//            var question = this.ui.streamList.find('.question').first();
//            if (question.length) {
//                this.ui.streamList.prepend(question);
//            }

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
//        this.ui.streamFooter.addClass('in');
        this.ui.streamFooter.find('.static-spinner').removeClass('hide');
        this.ui.streamFooter.removeClass('clickable');
    }

    var hideLoadingMore = function() {
        this.ui.streamFooter.find('.static-spinner').addClass('hide');
        this.ui.streamFooter.addClass('clickable');
    }

    var showNoMoreToLoad = function() {
        this.ui.streamFooter.find('.static-spinner').removeClass('hide');
        this.ui.streamFooter.removeClass('clickable');
        this.ui.streamFooter.text("That's all we have, folks.");
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
                hideLoadingMore.apply(self);
            } else {
                console.log('No more items');
                showNoMoreToLoad.apply(self);
                noMoreItems = true;
            }

            loadingMoreItems = false;
        });

        request.error(function(xhr) {
            console.log("Error loading items", xhr);
            hideLoadingMore.apply(self);

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
            created = dtutils.time_ago(created);
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

            $this.find('.answer-list')
                //We already have css to hide the box, but this will let the collapse plugin function later
                .addClass('collapse');

            //Store a map from the id to the element
            itemHash[$this.data('id')] = $this;

            //Process the created date if it exists
            var timeElement = $this.find(ITEM_CREATED_AT_SELECTOR)
            var created = timeElement.data('created');
            if (created) {
                timeElement.data('created', new Date(created * 1000));
            }

            var itemType = $this.data('type');
            switch (itemType) {
                case 'tweet':
                    //Tweet($this);
                    break;
                case 'question':
                    //Question($this);
                    break;
            }
        });
    }

    var attachEventHandlers = function () {
        this.on('show-pending-items', showPendingItems, this);

        var self = this;
        this.ui.streamFooter.on('click', function(e) {
            if (loadingMoreItems) {
                return;
            }

            checkForMore.apply(self);
        });
    }

    var StreamPanel = function () {
        attachInteractions.call(this);
        attachEventHandlers.call(this);
        startPoll.call(this);

        //move the most recent question to the top
//        var question = this.ui.streamList.find('.question').first()
//        if (question.length) {
//            this.ui.streamList.prepend(question);
//        }
        //Process initial stream items
        processItems.call(this, this.ui.streamList.children());
    };

    return StreamPanel;
});