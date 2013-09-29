define(function(require) {

    var $ = require('jquery');
    var IntervalSelection = require('modules/interval-selection');

    var INTERVAL_FIELD_SELECTOR = '.interval-field';

    var CreateApp = function() {
        this.intervalSelector = new IntervalSelection($(INTERVAL_FIELD_SELECTOR));
    };

    window.app = new CreateApp();
    return window.app;
});