(function() {

    var TIME_FORMAT = 'h:mma';
    var DATE_FORMAT = 'M/DD/YYYY';
    var DATE_PICKER_FORMAT = 'm/dd/yyyy';
    
    var INTERVAL_START_SELECTOR = '.interval-start';
    var INTERVAL_STOP_SELECTOR = '.interval-stop';
    var DATE_PICKER_SELECTOR = '.date-picker';
    var TIME_PICKER_SELECTOR = '.time-picker';
    
    var INVALID_CLASS = 'error';
    
    var DEFAULT_DURATION = 60*60; //1 hour in seconds
    var NUM_HALFS_TO_INCLUDE = 2;
    
    var IntervalSelection = function(element) {
        
        this.element = element;
        
        this.initUI();
        this.attachEvents();
        this.initPickers();
        this.initDataModel();
        this.attachWidgetEvents();
    }
    
    IntervalSelection.prototype.initDataModel = function() {
        this.model = {};
        
        var startTime = this.element.data('start-timestamp');
        var stopTime = this.element.data('stop-timestamp');
        var utcOffset = this.element.data('utc-offset');
        var timezone = this.element.data('timezone');
        
        if (startTime && stopTime) {
            this.model.startTime = moment.unix(startTime);
            this.model.duration = stopTime - startTime;
            this.model.stopTime = moment.unix(stopTime);
        } else if (startTime) {
            this.model.startTime = moment.unix(startTime);
            this.model.duration = DEFAULT_DURATION;
            this.model.stopTime = moment.unix(startTime + DEFAULT_DURATION);
            
            this.updateStop();
            
        } else {
            //Initialize to the next whole hour after the current time
            var theHour = moment()
            theHour.startOf('hour')
            theHour.add('hours', 1)
        
            this.model.startTime = theHour;
            this.model.duration = DEFAULT_DURATION;
            this.model.stopTime = moment.unix(theHour.unix() + DEFAULT_DURATION)
            
            this.setStartDateTime(this.model.startTime);
        }
        
        if (utcOffset) {
            this.model.utcOffset = utcOffset;
        } else {
            this.model.utcOffset = null;
        }
        
        if (timezone) {
            this.model.timezone = timezone;
        } else {
            this.model.timezone = null;
        }
    }
    
    IntervalSelection.prototype.initUI = function() {
        this.ui = {};
        
        this.ui.intervalStartGroup = this.element.find(INTERVAL_START_SELECTOR);
        this.ui.intervalStopGroup = this.element.find(INTERVAL_STOP_SELECTOR);
        
        this.ui.startDatePicker = this.ui.intervalStartGroup.find(DATE_PICKER_SELECTOR);
        this.ui.startTimePicker = this.ui.intervalStartGroup.find(TIME_PICKER_SELECTOR);
        this.ui.stopDatePicker = this.ui.intervalStopGroup.find(DATE_PICKER_SELECTOR);
        this.ui.stopTimePicker = this.ui.intervalStopGroup.find(TIME_PICKER_SELECTOR);
        
        this.ui.startDate = this.ui.startDatePicker.find('input');
        this.ui.startTime = this.ui.startTimePicker.find('input');
        this.ui.stopDate = this.ui.stopDatePicker.find('input');
        this.ui.stopTime = this.ui.stopTimePicker.find('input');
    }
    
    IntervalSelection.prototype.setStopDateTime = function(time, dontUpdateStop) {
        //Calculate the difference against the start time
        this.model.duration = time.unix() - this.model.startTime.unix();
        this.model.stopTime = time;
        
        this.checkValidity();
        
        dontUpdateStop || this.updateStop();
    }
    
    IntervalSelection.prototype.checkValidity = function() {
        //Mark times invalid if needed
        this.validSelection = this.model.duration > 0;
        this.ui.intervalStopGroup.toggleClass(INVALID_CLASS, !this.validSelection);
    }

    IntervalSelection.prototype.setStartDateTime = function(time, dontUpdateStop) {
        
        this.model.startTime = time;
        
        if (!this.validSelection) {
            //If the selection isn't valid, then let the start time alter the duration
            this.model.duration = this.model.stopTime.unix() - this.model.startTime.unix();
            this.checkValidity();
        } else {
            //Update the stop time keeping duration constant
            this.model.stopTime = moment.unix(this.model.startTime.unix() + this.model.duration);
        }
        
        var dateStr = this.model.startTime.format(DATE_FORMAT);
        this.ui.startDate.val(dateStr);
        this.ui.startDate.datepicker('update', dateStr);
        this.ui.stopDate.datepicker('setHighlightDate', this.model.startTime.toDate());
        
        var timeStr = this.model.startTime.format(TIME_FORMAT);
        this.ui.startTime.val(timeStr);
        
        this.ui.startDate.toggleClass(INVALID_CLASS, false);
        this.ui.startTime.toggleClass(INVALID_CLASS, false);
        
        var dateOfStart = getDateOnly(this.model.startTime);
        var timeSeries = rechattr.util.getHourlyTimes(dateOfStart);
        var selectedTime = nextNearestTime(this.model.startTime, timeSeries);
        this.ui.startTimePicker.dropdownmenu('menu', timeSeries);
        this.ui.startTimePicker.dropdownmenu('update', selectedTime);
        
        if (!this.validSelection) {
            //Leave the stop time display alone if the duration is not valid
            return;
        }
        
        dontUpdateStop || this.updateStop();
    }
    
    IntervalSelection.prototype.updateStop = function() {
        
        //If it is the same day as the start, save a flag
        this.sameDay = this.model.stopTime.isSame(this.model.startTime, 'day')
        
        
        var dateStr = this.model.stopTime.format(DATE_FORMAT);
        this.ui.stopDate.val(dateStr);
        this.ui.stopDate.datepicker('update', dateStr);   
        this.ui.startDate.datepicker('setHighlightDate', this.model.stopTime.toDate());
        
        var timeStr = this.model.stopTime.format(TIME_FORMAT);
        this.ui.stopTime.val(timeStr);
        
        
        var timeSeries;
        if (this.sameDay) {
            //Generate a set of times only after the current START time
            timeSeries = rechattr.util.getHourlyTimes(this.model.startTime, NUM_HALFS_TO_INCLUDE);
        } else {
            //Generate a set of times on the day of the current stop time
            var dateOfStop = getDateOnly(this.model.stopTime);
            timeSeries = rechattr.util.getHourlyTimes(dateOfStop);
        }
        
        //Get the time right after the stop time for the menu
        var selectedTime = nextNearestTime(this.model.stopTime, timeSeries);
        this.ui.stopTimePicker.dropdownmenu('menu', timeSeries);
        this.ui.stopTimePicker.dropdownmenu('update', selectedTime);
        
        this.ui.stopDate.toggleClass(INVALID_CLASS, false);
        this.ui.stopTime.toggleClass(INVALID_CLASS, false);
    }
    
    function getDateOnly(mo) {
        return mo.clone().startOf('day');
    }
    
    function setDateOnly(on, from) {
        on = on.clone();
        on.date(from.date());
        on.month(from.month());
        on.year(from.year());
        return on;
    }
    
    function setTimeOnly(on, from) {
        on = on.clone();
        on.hour(from.hour());
        on.minute(from.minute());
        on.second(from.second());
        return on;
    }
    
    IntervalSelection.prototype.attachWidgetEvents = function() {
        var self = this;
        this.ui.stopDate.on('changeDate', function(e) {
            var dateOnly = moment(e.date).utc();
            var dateTime = setDateOnly(self.model.stopTime, dateOnly);
            self.setStopDateTime(dateTime, false);
        });
        
        this.ui.startDate.on('changeDate', function(e) {
            var dateOnly = moment(e.date).utc();
            var dateTime = setDateOnly(self.model.startTime, dateOnly);
            self.setStartDateTime(dateTime);
        });
        
        this.ui.stopTimePicker.on('dropdown.select', function(e, time) {
            var dateTime = setTimeOnly(self.model.stopTime, time);
            self.setStopDateTime(dateTime);
            
            self.ui.stopTimePicker.dropdownmenu('hide');
        });
        
        this.ui.startTimePicker.on('dropdown.select', function(e, time) {
            var dateTime = setTimeOnly(self.model.startTime, time);
            self.setStartDateTime(dateTime);
            
            self.ui.startTimePicker.dropdownmenu('hide');
        });
    }
    
    function parseDate(userDate) {
        var date = moment(userDate, DATE_FORMAT);
        if (date && date.isValid()) {
            return date;
        }
    }
    
    function parseTime(userTime) {
        var time = moment(userTime, TIME_FORMAT);
        if (time && time.isValid()) {
            return time;
        }
    }
    
    IntervalSelection.prototype.attachEvents = function() {
        var self = this;
        
        $(document).on('click', function(e) {
            if (!self.ui.startTimePicker.find(e.target).size()) {
                self.ui.startTimePicker.dropdownmenu('hide');
            }
            if (!self.ui.stopTimePicker.find(e.target).size()) {
                self.ui.stopTimePicker.dropdownmenu('hide');
            }
        });
        
        this.ui.startTime
        .on('blur', function(e) {
            // Hide if no child is active (i.e. being clicked)
            if (!self.ui.startTimePicker.find(":active").size()) {
                self.ui.startTimePicker.dropdownmenu('hide');
            }
        })
        .on('focus', function(e) {
            self.ui.startTimePicker.dropdownmenu('show');
        })
        .on('change', function(e) {
            var timeOnly = $(this).val();
            timeOnly = parseTime(timeOnly)
            if (timeOnly) {
                var dateTime = setTimeOnly(self.model.startTime, timeOnly);
                self.setStartDateTime(dateTime);
            } else {
                self.startTime.toggleClass(INVALID_CLASS, true);
            }
        });
        
        this.ui.startDate
        .on('change', function(e) {
            var dateOnly = $(this).val();
            dateOnly = parseDate(dateOnly);
            if (dateOnly) {
                var dateTime = setDateOnly(self.model.startTime, dateOnly);
                self.setStartDateTime(dateTime);
            } else {
                self.startDate.toggleClass(INVALID_CLASS, true);
            }
            self.ui.startDate.datepicker('hide');
        });
        
        this.ui.stopTime
        .on('blur', function(e) {
            // Hide if no child is active (i.e. being clicked)
            if (!self.ui.stopTimePicker.find(":active").size()) {
                self.ui.stopTimePicker.dropdownmenu('hide');
            }
        })
        .on('focus', function(e) {
            self.ui.stopTimePicker.dropdownmenu('show');
        })
        .on('change', function(e) {
            var timeOnly = $(this).val();
            timeOnly = parseTime(timeOnly);
            if (timeOnly) {
                var dateTime = setTimeOnly(self.model.stopTime, timeOnly);
                self.setStopDateTime(dateTime);
            } else {
                self.ui.stopTime.toggleClass(INVALID_CLASS, true);
            }
        });
        
        this.ui.stopDate
        .on('change', function(e) {
            var dateOnly = $(this).val();
            dateOnly = parseDate(dateOnly);
            if (dateOnly) {
                var dateTime = setDateOnly(self.model.stopTime, dateOnly);
                self.setStopDateTime(dateTime);
                self.ui.stopDate.toggleClass(INVALID_CLASS, false);
            } else {
                self.ui.stopDate.toggleClass(INVALID_CLASS, true);
            }
            self.ui.stopDate.datepicker('hide');
        });
        
    }
    
    function nextNearestTime(time, fromTimes, dateInsensitive) {
        var before = null;
        $.each(fromTimes, function(index, value) {
            if (time - value >= 0) {
                //update before until it passes time
                before = value;
            } else {
                return false;
            }
        });
        
        return before;
    }
    
    IntervalSelection.prototype.initPickers = function() {
        //Prepare the time pickers for menu-ization
        var timePickers = this.ui.startTimePicker.add(this.ui.stopTimePicker)
        timePickers
        .addClass('dropdown');
        // .addClass('input-append dropdown')
        // .append('<div class="btn dropdown-toggle"><span class="icon-time"></span></div>');
    
        this.ui.startTimePicker.dropdownmenu({
            display: function(time) {
                return time.format(TIME_FORMAT);
            }
        });
        
        var self = this;
        this.ui.stopTimePicker.dropdownmenu({
            display: function(time) {
                if (self.sameDay) {
                    //When the same day is showing on both start and end,
                    //only show the options in the future on the time selector
                    var objTime = setDateOnly(time, self.model.stopTime);
                    var offset = objTime.diff(self.model.startTime);
                    if (offset < 0) {
                        return false;
                    }
                    var minutes = time.diff(self.model.startTime, 'minutes');
                    
                    var diff = ' (';
                    if (minutes < 60) {
                        diff += minutes + ' mins';
                    } else {
                        hours = minutes / 60;
                        diff += hours;
                        if (hours != 1) {
                            diff += " hrs";
                        } else {
                            diff += " hr";
                        }
                    }
                    
                    diff += ')';
                    
                    return time.format(TIME_FORMAT) + diff;
                }
                return time.format(TIME_FORMAT);
            }
        });
        
        this.ui.startDate.add(this.ui.stopDate)
        .datepicker({
            format: DATE_PICKER_FORMAT,
            forceParse: false,
            keyboardNavigation: false,
            todayHighlight: true,
            highlightInterval: true,
            autoclose: true
        });
        
    }

    // CreateApp.prototype.updateMenuFromInput = function(inputElement, menuElement) {
        // var input = $(inputElement);
        // var menu = $(menuElement);
        
        // var time = moment(input.val(), TIME_FORMAT)
        // if (time.isValid()) {
            // var formatted = time.format(TIME_FORMAT);
            // var index = this.hours.indexOf(formatted);
            // if (index >= 0) {
                // menu.dropdownmenu('setActiveIndex', index);
            // } else {
                // time.startOf('hour');
                // formatted = time.format(TIME_FORMAT);
                // index = this.hours.indexOf(formatted);
                // menu.dropdownmenu('scrollToIndex', index);
                // menu.dropdownmenu('setActiveIndex', false);
            // }
        // } else {
            // input.val('');
        // };
    // }

    // CreateApp.prototype.initializeDefaultTimes = function() {
        
        // var now = moment();
        
        // var theHour = now.clone()
        // theHour.startOf('hour')
        // theHour.add('hours', 1)
        
        // if (!this.$startTime.val() && !this.$startDate.val()) {
            // this.$startTime.val(theHour.format(TIME_FORMAT));
            // this.$startDate.val(theHour.format(DATE_FORMAT));
        // }
        
        // if (!this.$stopTime.val() && !this.$stopDate.val()) {
            // theHour.add('seconds', this.duration)
            // this.$stopTime.val(theHour.format(TIME_FORMAT));
            // this.$stopDate.val(theHour.format(DATE_FORMAT));
        // }
    // }
    
    rechattr.util.IntervalSelection = IntervalSelection;
    return IntervalSelection;
})()