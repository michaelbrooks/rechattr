define(function(require) {
    var $ = require('jquery');
    var events = require('util/events');

    var TIME_FORMAT = 'h:mma';
    var DATE_FORMAT = 'M/DD/YYYY';
    var DATE_PICKER_FORMAT = 'm/dd/yyyy'
    
    var DEFAULT_DURATION = 60*60; //1 hour in seconds
    
    var TIMELINE_SELECTOR = '.timeline';
    var TIMELINE_LINE_SELECTOR = '.timeline-line';
    var TIMELINE_FOCUS_SELECTOR = '.timeline-focus';
    var TIMELINE_BEAD_SELECTOR = '.timeline-bead';
    
    var Timeline = function(wrapper) {
        this.initUI(wrapper);
        
        this.attachEvents();
    }
    
    Timeline.prototype.initUI = function(wrapper) {
        this.ui = {};
        
        this.ui.wrapper = wrapper;
        this.ui.timeline = this.ui.wrapper.find(TIMELINE_SELECTOR);
        this.ui.timelineLine = this.ui.timeline.find(TIMELINE_LINE_SELECTOR);
        this.ui.timelineFocus = this.ui.timeline.find(TIMELINE_FOCUS_SELECTOR);
    }
    
    Timeline.prototype.createBead = function(x, y) {
        var percentThrough = x / this.ui.wrapper.width();
        
        var bead = $('<div>')
        .addClass('timeline-bead')
        .css('left', (100 * percentThrough) + '%');
        
        this.trigger('new-bead', bead, percentThrough);
        
        this.ui.timeline.append(bead);
        
        this.selectBead(bead);
    }
    
    Timeline.prototype.deleteBead = function(bead) {
        if (this.selected == bead) {
            this.selected = null;
        }
        if (this.dragging == bead) {
            this.dragging = null;
        }
        
        bead.remove();
    }
    
    Timeline.prototype.selectBead = function(bead) {
        if (this.selected) {
            this.trigger('deselect', this.selected);
            this.selected.removeClass('selected');
        }
    
        this.trigger('select', bead);
        
        this.selected = bead;
        this.selected.addClass('selected');
    }

    Timeline.prototype.startDragging = function(bead) {
        this.trigger('drag-start', bead);
        
        this.dragging = bead;
        this.dragging.addClass('dragging');
        this.ui.timelineFocus.removeClass('in');
        
        this.selectBead(bead);
    }
    
    Timeline.prototype.stopDragging = function(bead) {
        this.trigger('drag-stop', bead);
        
        this.dragging.removeClass('dragging');
        this.dragging = null;
    }
    
    Timeline.prototype.attachEvents = function() {
        var self = this;
        this.ui.wrapper.on('mousemove', function(e) {
            var width = self.ui.wrapper.width();
            var offset = self.ui.wrapper.offset();
            var x = e.pageX - offset.left;
            var y = e.pageY - offset.top;
            
            if (x < 0) {
                x = 0;
            } else if (x > width) {
                x = width
            }
            
            var positioned = self.ui.timelineFocus;
            
            if (self.dragging) {
                positioned = self.dragging;
            }
            
            var percentThrough = x / self.ui.wrapper.width();
            positioned.css('left', (100 * percentThrough) + "%");
        })
        .on('mouseover', function(e) {
            if (!self.dragging) {
                self.ui.timelineFocus.addClass('in');
            }
        })
        .on('mouseout', function(e) {
            self.ui.timelineFocus.removeClass('in');
        })
        .on('click', function(e) {
            var offset = self.ui.wrapper.offset();
            var x = e.pageX - offset.left;
            var y = e.pageY - offset.top;
            
            self.createBead(x, y);
        })
        .on('click', TIMELINE_BEAD_SELECTOR, function(e) {
            self.selectBead($(this));
            e.preventDefault();
            return false;
        })
        .on('mousedown', TIMELINE_BEAD_SELECTOR, function(e) {
            self.startDragging($(this))
            
            e.preventDefault();
            return false;
        });
        
        $(document).on('mouseup', function(e) {
            if (self.dragging) {
                self.stopDragging();
            }
        });
        
    }

    events(Timeline)

    return Timeline;
});