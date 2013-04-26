define(function () {
    var dtutils = {};

    /**
     * Generates a list of hourly times.
     */
    dtutils.getHourlyTimes = function (timeFrom, numHalfsToInclude) {
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
    }

    return dtutils;
});