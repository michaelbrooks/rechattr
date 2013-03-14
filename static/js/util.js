(function() {

    var util = {};

    util.showOverlay = function(message) {
        var loadingOverlay = $('.overlay').show();
        setTimeout(function() {
            loadingOverlay.find('.message').text(message);
            loadingOverlay.addClass('in');
        }, 1);
    }
    
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
    
    rechattr.util = util;
    
    return util;
})();