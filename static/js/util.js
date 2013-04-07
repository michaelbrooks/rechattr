(function() {
    var FLASH_SELECTOR = '.flash';
    var FLASH_TYPE_MAP = {'error': 'alert-danger', 'warn': 'alert-warning', 'info': 'alert-info', 'success': 'alert-success'};
    var FLASH_TIMEOUT = 2000;
    
    var util = {};

    /**
	 * Generates a list of hourly times.
	 */
	util.getHourlyTimes = function(timeFrom, numHalfsToInclude) {
        numHalfsToInclude = numHalfsToInclude | 0;
        
		var times = [];
		var time = timeFrom.clone()
		for (var h = time.hour(); h < 24; h++) {
            times.push(time.clone());
            
            if (numHalfsToInclude > 0) {
                //While still halfs to include interject a half-hour in there
                times.push(time.clone().add('minutes', 30));
                numHalfsToInclude--;
            }
            
            time.add('hours', 1);
		}
		
		return times;
	}
    
    var closeButton = '<div class="close">&times;</div>'
    var flashMessage = function(options) {
        var cls = FLASH_TYPE_MAP[options.type];
        var alert = $("<div>").addClass('alert fade ' + cls);
        alert.append(closeButton);
        alert.append(options.message);
        return alert;
    }
    
    var flashBox = null;
    var flashTimeout = null;
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
        
        //Initialize the flash if there is one
        var alert = flashBox.find('.alert');
        if (alert.size()) {
            alert.alert();
            if (flashTimeout) {
                clearTimeout(flashTimeout);
            }
            flashTimeout = setTimeout(util.hideFlash, FLASH_TIMEOUT);
        }
    }
    
    util.flash = function(options) {
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
        setTimeout(function() {
            alert.addClass('in')
        }, 1);
        
        if (flashTimeout) {
            clearTimeout(flashTimeout);
        }
        flashTimeout = setTimeout(util.hideFlash, FLASH_TIMEOUT);
    }
    
    util.flash.error = function(message) {
        return util.flash({
            'type': 'error',
            'message': message
        });
    }
    
    util.hideFlash = function() {
        flashBox.find('.alert').addClass('very-slow-fade').alert('close');
        flashTimeout = null;
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
    
    //See http://stackoverflow.com/questions/2593637/how-to-escape-regular-expression-in-javascript
    util.regex_quote = function(str) {
        return (str+'').replace(/([.?*+^$[\]\\(){}|-])/g, "\\$1");
    };
    
    util.twitter = {};
    var tr = util.twitter.regex = {}
    
    //See https://raw.github.com/twitter/twitter-text-java/master/src/com/twitter/Regex.java
    tr.LATIN_ACCENTS_CHARS = "\\u00c0-\\u00d6\\u00d8-\\u00f6\\u00f8-\\u00ff" + // Latin-1
                                              "\\u0100-\\u024f" + // Latin Extended A and B
                                              "\\u0253\\u0254\\u0256\\u0257\\u0259\\u025b\\u0263\\u0268\\u026f\\u0272\\u0289\\u028b" + // IPA Extensions
                                              "\\u02bb" + // Hawaiian
                                              "\\u0300-\\u036f" + // Combining diacritics
                                              "\\u1e00-\\u1eff"; // Latin Extended Additional (mostly for Vietnamese)
    tr.HASHTAG_ALPHA_CHARS = "a-z" + tr.LATIN_ACCENTS_CHARS +
                           "\\u0400-\\u04ff\\u0500-\\u0527" +  // Cyrillic
                           "\\u2de0-\\u2dff\\ua640-\\ua69f" +  // Cyrillic Extended A/B
                           "\\u0591-\\u05bf\\u05c1-\\u05c2\\u05c4-\\u05c5\\u05c7" +
                           "\\u05d0-\\u05ea\\u05f0-\\u05f4" + // Hebrew
                           "\\ufb1d-\\ufb28\\ufb2a-\\ufb36\\ufb38-\\ufb3c\\ufb3e\\ufb40-\\ufb41" +
                           "\\ufb43-\\ufb44\\ufb46-\\ufb4f" + // Hebrew Pres. Forms
                           "\\u0610-\\u061a\\u0620-\\u065f\\u066e-\\u06d3\\u06d5-\\u06dc" +
                           "\\u06de-\\u06e8\\u06ea-\\u06ef\\u06fa-\\u06fc\\u06ff" + // Arabic
                           "\\u0750-\\u077f\\u08a0\\u08a2-\\u08ac\\u08e4-\\u08fe" + // Arabic Supplement and Extended A
                           "\\ufb50-\\ufbb1\\ufbd3-\\ufd3d\\ufd50-\\ufd8f\\ufd92-\\ufdc7\\ufdf0-\\ufdfb" + // Pres. Forms A
                           "\\ufe70-\\ufe74\\ufe76-\\ufefc" + // Pres. Forms B
                           "\\u200c" +                        // Zero-Width Non-Joiner
                           "\\u0e01-\\u0e3a\\u0e40-\\u0e4e" + // Thai
                           "\\u1100-\\u11ff\\u3130-\\u3185\\uA960-\\uA97F\\uAC00-\\uD7AF\\uD7B0-\\uD7FF" + // Hangul (Korean)
                           "\\p{InHiragana}\\p{InKatakana}" +  // Japanese Hiragana and Katakana
                           "\\p{InCJKUnifiedIdeographs}" +     // Japanese Kanji / Chinese Han
                           "\\u3003\\u3005\\u303b" +           // Kanji/Han iteration marks
                           "\\uff21-\\uff3a\\uff41-\\uff5a" +  // full width Alphabet
                           "\\uff66-\\uff9f" +                 // half width Katakana
                           "\\uffa1-\\uffdc";                  // half width Hangul (Korean)
    tr.HASHTAG_ALPHA_NUMERIC_CHARS = "0-9\\uff10-\\uff19_" + tr.HASHTAG_ALPHA_CHARS;
    tr.HASHTAG_ALPHA = "[" + tr.HASHTAG_ALPHA_CHARS +"]";
    tr.HASHTAG_ALPHA_NUMERIC = "[" + tr.HASHTAG_ALPHA_NUMERIC_CHARS +"]";
    
    tr.VALID_HASHTAG = new RegExp("(^|[^&" + 
                                  tr.HASHTAG_ALPHA_NUMERIC_CHARS +
                                  "])(#|\uFF03)(" + 
                                  tr.HASHTAG_ALPHA_NUMERIC + 
                                  "*" + 
                                  tr.HASHTAG_ALPHA + 
                                  tr.HASHTAG_ALPHA_NUMERIC + "*)", "i");
    tr.VALID_HASHTAG_GROUP_BEFORE = 1;
    tr.VALID_HASHTAG_GROUP_HASH = 2;
    tr.VALID_HASHTAG_GROUP_TAG = 3;
    tr.INVALID_HASHTAG_MATCH_END = new RegExp("^(?:[#\\uFF03]|://)");
    
    util.twitter.hashtag_contains = function(hashtag) {
        var htmatch = hashtag.match(tr.VALID_HASHTAG);
        if (!htmatch) {
            throw "Invalid hashtag";
        }
        
        hashtag = htmatch[tr.VALID_HASHTAG_GROUP_TAG];
        
        var hashtagRegex = new RegExp("(^|[^0-9A-Z&/]+)(#|\uFF03)(" + 
                                      hashtag + 
                                      ")($|[^#\uFF03" + tr.HASHTAG_ALPHA_NUMERIC_CHARS + "])", 
                                      "i");
        return function(inputStr) {
            return inputStr.match(hashtagRegex);
        }
    }
    
    util.url = {}
    util.url.current = document.location.href;
    util.url.extend = function() {
        var segments = Array.prototype.join.call(arguments, '/');
        return util.url.current + '/' + segments;
    }
    
    rechattr.util = util;
    
    return util;
})();