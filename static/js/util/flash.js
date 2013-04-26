define(function (require) {
    var $ = require('jquery');
    require('vendor/bootstrap');

    var FLASH_SELECTOR = '.flash';
    var FLASH_TYPE_MAP = {'error': 'alert-danger', 'warn': 'alert-warning', 'info': 'alert-info', 'success': 'alert-success'};
    var FLASH_TIMEOUT = 2000;

    var closeButton = '<div class="close">&times;</div>'
    var flashMessage = function (options) {
        var cls = FLASH_TYPE_MAP[options.type];
        var alert = $("<div>").addClass('alert fade ' + cls);
        alert.append(closeButton);
        alert.append(options.message);
        return alert;
    }

    var flashBox = null;
    var flashTimeout = null;

    var flash = {
        initFlash: function () {
            flashBox = $(FLASH_SELECTOR);

            //Clicking the flash box closes the alert also
            flashBox.on('click', function () {
                flashBox.find('.alert').alert('close');
            });

            //When an alert closes, make sure to hide the flash box
            $(document).on('closed', FLASH_SELECTOR + ' .alert', function () {
                flashBox.hide();
            });

            //Initialize the flash if there is one
            var alert = flashBox.find('.alert');
            if (alert.size()) {
                alert.alert();
                if (flashTimeout) {
                    clearTimeout(flashTimeout);
                }
                flashTimeout = setTimeout(flash.hideFlash, FLASH_TIMEOUT);
            }
        },
        flash: function (options) {
            if (!flashBox) {
                console.log("util.flash() called before util.initFlash()")
                return;
            }
            var alert = flashMessage(options);

            flashBox
                .html(alert)
                .show();

            alert
                .alert();

            // Display a bit later to allow the element to exist first
            setTimeout(function () {
                alert.addClass('in')
            }, 1);

            if (flashTimeout) {
                clearTimeout(flashTimeout);
            }
            flashTimeout = setTimeout(flash.hideFlash, FLASH_TIMEOUT);
        },
        error: function (message) {
            return flash.flash({
                'type': 'error',
                'message': message
            });
        },
        success: function (message) {
            return flash.flash({
                'type': 'success',
                'message': message
            });
        },
        hideFlash: function () {
            flashBox.find('.alert').addClass('very-slow-fade').alert('close');
            flashTimeout = null;
        }
    }

    return flash;
});