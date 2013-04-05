(function() {

    var TIME_FORMAT = 'h:mma';
    var DATE_FORMAT = 'M/DD/YYYY';
    var DATE_PICKER_FORMAT = 'm/dd/yyyy'
    
    var DEFAULT_DURATION = 60*60; //1 hour in seconds
    
    var INTERVAL_FIELD_SELECTOR = '.interval-field';
    
    
    var EditApp = function() {
        var self = this;
        
        this.intervalSelector = new rechattr.util.IntervalSelection($(INTERVAL_FIELD_SELECTOR));
    }

    rechattr.classes.EditApp = EditApp;
    return EditApp;
})()