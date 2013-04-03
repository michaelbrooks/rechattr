(function() {

    var TIME_FORMAT = 'h:mma';
    var DATE_FORMAT = 'M/DD/YYYY';
    var DATE_PICKER_FORMAT = 'm/dd/yyyy'
    
    var DEFAULT_DURATION = 60*60; //1 hour in seconds
    
    var CreateApp = function() {
        var self = this;
        
        this.$form = $('form');
        this.gmtOffset = -new Date().getTimezoneOffset();
        $('input[name=gmt_offset]').val(this.gmtOffset);
        
        this.hours = rechattr.util.getHourlyTimes(TIME_FORMAT);
        
        this.duration = DEFAULT_DURATION;
        
        this.$startDate = $('.start-date');
        this.$startDatePicker = this.$startDate.parent();
        
        this.$stopDate = $('.stop-date');
        this.$stopDatePicker = this.$stopDate.parent();
        
        this.$startTime = $('.start-time');
        this.$stopTime = $('.stop-time');
        
        this.initializeDefaultTimes();
        this.initializeDatePickers();
        this.initializeTimePickers();
        // this.initializeConstraints();
    }

    CreateApp.prototype.initializeTimePickers = function() {
        var self = this;
        
        $('.time-picker')
        .addClass('input-append dropdown')
        .append('<div class="btn dropdown-toggle"><span class="icon-time"></span></div>')
        .dropdownmenu({
            choices: this.hours,
            display: function(time) {
                return time.format(TIME_FORMAT);
            }
        })
        .on('dropdown.select', function(event, time) {
            var input = $(this).find('input');
            input.val(time);
            self.updateMenuFromInput(input[0], this);
        })
        .each(function(index, timePickerElem) {
            var timePicker = $(timePickerElem);
            var input = timePicker.find('input');
            
            self.updateMenuFromInput(input[0], timePickerElem);
            
            input.on('change', function(event) {
                self.updateMenuFromInput(this, timePickerElem);
            });
        });
    }

    CreateApp.prototype.updateMenuFromInput = function(inputElement, menuElement) {
        var input = $(inputElement);
        var menu = $(menuElement);
        
        var time = moment(input.val(), TIME_FORMAT)
        if (time.isValid()) {
            var formatted = time.format(TIME_FORMAT);
            var index = this.hours.indexOf(formatted);
            if (index >= 0) {
                menu.dropdownmenu('setActiveIndex', index);
            } else {
                time.startOf('hour');
                formatted = time.format(TIME_FORMAT);
                index = this.hours.indexOf(formatted);
                menu.dropdownmenu('scrollToIndex', index);
                menu.dropdownmenu('setActiveIndex', false);
            }
        } else {
            input.val('');
        };
    }

    CreateApp.prototype.initializeDefaultTimes = function() {
        
        var now = moment();
        
        var theHour = now.clone()
        theHour.startOf('hour')
        theHour.add('hours', 1)
        
        if (!this.$startTime.val() && !this.$startDate.val()) {
            this.$startTime.val(theHour.format(TIME_FORMAT));
            this.$startDate.val(theHour.format(DATE_FORMAT));
        }
        
        if (!this.$stopTime.val() && !this.$stopDate.val()) {
            theHour.add('seconds', this.duration)
            this.$stopTime.val(theHour.format(TIME_FORMAT));
            this.$stopDate.val(theHour.format(DATE_FORMAT));
        }
    }

    CreateApp.prototype.initializeDatePickers = function() {
        var self = this;
        
        $('.date-picker')
        .addClass('input-append date')
        .append('<div class="btn"><span class="icon-calendar"></span></div>')
        .datepicker({
            format: DATE_PICKER_FORMAT
        })
        .find('input')
        .on('change', function() {
            var val = $(this).val();
            $(this).parent().datepicker('update', val);
        });
    }
    
    CreateApp.prototype.getStartDateTime = function() {
        return moment(
                      this.$startDate.val() + " " + this.$startTime.val(), 
                      DATE_FORMAT + " " + TIME_FORMAT);
    }
    
    CreateApp.prototype.getStopDateTime = function() {
        return moment(
                      this.$stopDate.val() + " " + this.$stopTime.val(), 
                      DATE_FORMAT + " " + TIME_FORMAT);
    }
    
    rechattr.classes.CreateApp = CreateApp;
    return CreateApp;
})()