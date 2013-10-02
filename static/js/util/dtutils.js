define(function () {
    var dtutils = {};

    /**
     * Generates a list of hourly times.
     */
    dtutils.getHourlyTimes = function (timeFrom, numHalfsToInclude) {
        numHalfsToInclude = numHalfsToInclude | 0;

        var times = [];
        var time = timeFrom.clone();
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
    };


    var intervals = {
        zeroTime: 0,
        oneMinute: 60,
        oneHour: 60 * 60,
        oneDay: 60 * 60 * 24
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

    dtutils.time_ago = function (date) {
        var now = new Date();
        var delta = (now - date) / 1000;

        if (delta < intervals.zeroTime) {
            return "0s";
        } else if (delta < intervals.oneMinute) {
            return Math.round(delta).toString() + "s";
        } else if (delta < intervals.oneHour) {
            return Math.round(delta / 60).toString() + "m";
        } else if (delta < intervals.oneDay) {
            return Math.round(delta / (60 * 60)).toString() + "h";
        } else {
            return date.getDate().toString() + " " + monthMap[date.getMonth()];
        }
    };

    //Just putting all of these in a function so they don't interfere with anybody else
    (function () {
        /*
         * Builds a regex like this, for days: /(^|,|\s)(\d+)\s*(d|days?)($|,|\s)/
         * (^|,|\s)     -- start of string, a comma separator, or space
         * (\d+)        -- digits
         * \s*          -- optional whitespace
         * (d|days?)    -- single 'd' or 'day' or 'days'
         * ($|,|\s)     -- end of string, comma separator, or space
         */
        function buildRegex(unit) {
            return new RegExp("(^|,|\\s)(\\d+)\\s*(" + unit[0] + "|" + unit + "s?)($|,|\\s)");
        }
        var matchIndex = 2; //the 3rd part of the match (whole, group1, group2...)

        var units = [
            ['day', 60 * 60 * 24],
            ['hour', 60 * 60],
            ['minute', 60],
            ['second', 1]
        ];

        var rexes = units.map(function (unit) {
            return buildRegex(unit[0]);
        });

        //Export this value
        dtutils.offset = {
            //Expects something like "5 minutes, 32 seconds", like is produced by offset.format()
            parse: function (timeStr) {
                return units.reduce(function (prev, unit, index) {
                    var match = rexes[index].exec(timeStr);

                    if (match) {
                        match = Number(match[matchIndex]);
                        if (!isNaN(match)) {
                            return prev + match * unit[1]; // multiply by the seconds conversion factor
                        }
                    }

                    return prev;
                }, null);
            },
            format: function (seconds) {
                if (seconds === null) {
                    return '';
                }

                var segments = [];

                units.forEach(function (unit, index) {
                    //convert the remaining seconds into this unit
                    var inUnit = Math.floor(seconds / unit[1]);

                    if (inUnit > 0) {

                        //Generate the label
                        var label = unit[0];
                        if (inUnit > 1) {
                            label += 's';
                        }

                        segments.push(inUnit + " " + label);

                        //these seconds are now taken
                        seconds -= inUnit * unit[1];
                    }
                });

                //And a nice little hack to wrap things up
                if (segments.length === 0) {
                    segments.push('0 seconds');
                }

                return segments.join(', ');
            }
        };
    })();

    (function() {
        var regex = new RegExp("(\\d\\d?)(:(\\d\\d))? ?(am|pm)?");//"(^|,|\\s)(\\d+)\\s*(" + unit[0] + "|" + unit + "s?)($|,|\\s)");
        var hourIndex = 1;
        var minuteIndex = 3;
        var ampmIndex = 4;

        dtutils.time = {
            //Expects times like "5:30pm", "2am", or "13:30"
            parse: function(timeStr) {
                var parts = timeStr.toLowerCase().match(regex);

                var hour = Number(parts[hourIndex]);
                var minute = Number(parts[minuteIndex] || 0);
                var ampm = parts[ampmIndex] || 'am';

                if (minute < 0 || minute > 59) {
                    return false;
                }

                if (ampm !== 'am' && ampm !== 'pm') {
                    return false;
                }

                if (ampm === 'pm') {
                    hour += 12;
                }

                if (hour < 1 || hour > 23) {
                    return false;
                }

                return {
                    hour: hour,
                    minute: minute
                };
            }

        };
    })();

    return dtutils;
});