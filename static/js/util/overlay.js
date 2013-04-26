define(function (require) {
    var $ = require('jquery');
    require('vendor/jquery.spin');
    require('vendor/bootstrap');

    /* from underscore.js */
    var _idCounter = 0;
    var uniqueId = function (prefix) {
        var id = ++_idCounter + '';
        return prefix ? prefix + id : id;
    };

    var makeOverlay = function (loading) {
        var $this = $(this);

        if ($this.data('overlayId')) {
            hideOverlay.call(this);
        }

        var overlayId = uniqueId('rc_overlay');

        var overlayEl = $('<div>').addClass('rc-overlay');
        overlayEl.toggleClass('loading', loading);
        overlayEl.attr('id', overlayId);

        $this.append(overlayEl);

        $this.data('overlayId', overlayId);

        setTimeout(function () {
            overlayEl.addClass('in');

            if (loading) {
                overlayEl.addClass('.loading')
                    .spin({
                        color: '#333',
                        hwaccel: true,
                        position: 'absolute',
                        radius: 8,
                        width: 4,
                        length: 13
                    });
            }
        }, 1);
    };

    var hideOverlay = function () {
        var $this = $(this);

        var overlayId = $this.data('overlayId');
        $this.removeData('overlayId');

        var overlayEl = $('#' + overlayId);

        if ($.support.transition) {
            overlayEl.one($.support.transition.end, function () {
                if (overlayEl.is('.loading')) {
                    overlayEl.spin(false);
                }
                overlayEl.remove();
            });
        } else {
            if (overlayEl.is('.loading')) {
                overlayEl.spin(false);
            }
        }
        overlayEl.removeClass('in').remove();
    }

    var overlay = {
        show: function (selection) {
            selection.each(makeOverlay);
        },
        showLoading: function (selection) {
            selection.each(function () {
                makeOverlay.call(this, true);
            });
        },
        hide: function (selection) {
            selection.each(hideOverlay);
        }
    };

    return overlay;
});