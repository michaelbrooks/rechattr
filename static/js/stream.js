(function() {
    var STREAM_INTERVAL_SECONDS = 20;
    var STREAM_URL = "/stream"

    var _checkStream = function() {
        var self = this;
        
        var since = this._lastCheck;
        var data = {
            since: since
        }
        
        var request = $.get(this._url, data, 'json');
        
        request.done(function(response) {
            if (typeof response === 'string') {
                response = JSON.parse(response)
            }
            
            self._lastCheck = response.time;
            if (response.items > 0) {
                self._callback(response.items, response.html);
            }
        });
    }
    
    var Stream = function(config) {
        var poll = config.poll || 'undefined';
        var time = config.time || 0
        
        this._url = poll + "/stream";
        this._callback = undefined;
        this._inverval = undefined;
        this._lastCheck = time;
    };
    
    /**
     * Callback should be of the form
     * function(numItems, itemHtml) {...}
     */
    Stream.prototype.done = function(fun) {
        this._callback = fun;
        return this;
    }
    
    Stream.prototype.start = function() {
        if (!this._callback) {
            console.log("No callback set up for stream");
            return;
        }
        
        var millis = STREAM_INTERVAL_SECONDS * 1000;
        var self = this;
        this._interval = setInterval(function() {
            _checkStream.call(self);
        }, millis);
    }
    
    Stream.prototype.stop = function() {
        if (this._interval) {
            clearInterval(this._interval);
        }
    }
    
    rechattr.util.Stream = Stream;
    return Stream;
})();