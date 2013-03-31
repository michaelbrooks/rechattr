(function() {
    var FLASH_SELECTOR = '.flash';
    var FLASH_TYPE_MAP = {'error': 'alert-danger', 'warn': 'alert-warning', 'info': 'alert-info', 'success': 'alert-success'};
    var util = {};

    /**
	 * Generates a list of hourly times.
	 */
	util.getHourlyTimes = function(timeFormat) {
		var times = [];
		
		var time = moment('0', 'h'); //0th hour
		
		for (var h = 0; h < 24; h++) {
			times.push(time.format(timeFormat));
			time.add('hours', 1);
		}
		
		return times;
	}
    
    var closeButton = '<div class="close">&times;</div>'
    var flashMessage = function(type, message) {
        var cls = FLASH_TYPE_MAP[type];
        var alert = $("<div>").addClass('alert ' + cls);
        alert.append(closeButton);
        alert.append(message);
        return alert;
    }
    
    var flashBox = null;
    util.initFlash = function() {
        flashBox = $(FLASH_SELECTOR);
        
        //Clicking the flash box closes the alert also
        flashBox.on('click', function() {
            flashBox.find('.alert').alert('close');
        });
        
        //When an alert closes, make sure to hide the flash box
        $(document).on('closed', FLASH_SELECTOR + ' .alert', function() {
            flashBox.hide();
        });
    }
    
    util.flash = function(options) {
        if (!flashBox) {
            console.log("util.flash() called before util.initFlash()")
            return;
        }
        var alert = flashMessage(options);
        
        flashBox
        .html(alert)
        .alert()
    }
    
    var intervals = {
        zeroTime: 0,
        oneMinute: 60,
        oneHour: 60*60,
        oneDay: 60*60*24
    };
    var monthMap = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec"
    ];
    util.time_ago = function(date) {
        var now = new Date();
        var delta = (now - date) / 1000;
            
        if (delta < intervals.zeroTime) {
            return "0s";
        } else if (delta < intervals.oneMinute) {
            return Math.round(delta).toString() + "s";
        } else if (delta < intervals.oneHour) {
            return Math.round(delta / 60).toString() + "m";
        } else if (delta < intervals.oneDay) {
            return Math.round(delta / (60*60)).toString() + "h";
        } else {
            return date.getDate().toString() + " " + monthMap[date.getMonth()];
        }
    }
    
    rechattr.util = util;
    
    return util;
})();