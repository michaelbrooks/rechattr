define(function(require) {

    var config = require('config');

    var url = {
        current: document.location.href,
        extend: function () {
            var segments = Array.prototype.join.call(arguments, '/');
            return url.current + '/' + segments;
        },
        poll: function() {
            var base = config.poll;

            var segments = Array.prototype.join.call(arguments, '/');
            return base + '/' + segments;
        }
    };

    return url;
});