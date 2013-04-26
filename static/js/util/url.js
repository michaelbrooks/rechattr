define(function () {

    var url = {
        current: document.location.href,
        extend: function () {
            var segments = Array.prototype.join.call(arguments, '/');
            return url.current + '/' + segments;
        }
    };

    return url;
});