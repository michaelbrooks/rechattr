;(function($, window, document, undefined) {

  'use strict'; // jshint ;_;

  // DropdownMenu PUBLIC CLASS DEFINITION
  var DropdownMenu = function(element, options) {
    this.choices = options.choices;
    this.scrollTargetIndex = options.scrollTargetIndex;
    this.$element = $(element);
    this._init();
  };

  DropdownMenu.prototype = {

    constructor: DropdownMenu,

    _init: function() {
      var self = this;
        
      this.$toggle = this.$element.is('.dropdown-toggle') ? this.$element : this.$element.find('.dropdown-toggle');
      if (!this.$toggle.length === 0) {
        throw 'Could not find a .dropdown-toggle element';
      }
      
      this.$dropdown = this.$element.is('.dropdown') ? this.$element : this.$element.parents('.dropdown');
      if (this.$dropdown.length === 0) {
        throw 'DropdownMenu must be created inside of a .dropdown element';
      }
      
      //Construct the menu itself
      this.buildMenu();
      
      //Create the Bootstrap dropdown behavior
      this.$toggle.attr('data-toggle', 'dropdown');
      this.$toggle.dropdown();
      
      this.$toggle.on('click.dropdown.data-api', $.proxy(this.toggleClicked, this));
    },
    
    toggleClicked: function(e) {
        this.scrollToTarget();
        return false;
    },
    
    buildMenu: function() {
        var self = this;
        
        this.$menu = $('<ul class="dropdown-menu">');
        this.$toggle.before(this.$menu);
        
        this.choices.forEach(function(item, index) {
            var choice = $('<li><a tabindex="-1" href="#">' + (item) + '</a></li>');
            self.$menu.append(choice);
            
            choice.on('click', function(event) {
                self.$element.trigger('dropdown.select', item);
            });
            
            if (index === self.scrollTargetIndex) {
                self.scrollTarget = choice;
            }
        });
    },
    setActiveIndex: function(activeIndex) {
        this.$menu.find('li.active').removeClass('active');
        if (activeIndex !== false) {
            this.$menu.find('li:eq(' + activeIndex + ')').addClass('active');
            this.scrollToIndex(activeIndex);
        }
    },
    
    setActive: function(activeItem) {
        this.setActiveIndex(this.options.indexOf(activeItem));
    },
    
    scrollToIndex: function (index) {
        this.scrollTarget = this.$menu.find('li:eq(' + index + ')');
        if (this.$dropdown.is('.open')) {
            this.scrollToTarget();
        }
    },
    
    scrollTo: function(item) {
        this.scrollToIndex(this.options.indexOf(item));
    },
    
    scrollToTarget: function() {
        if (this.scrollTarget && this.scrollTarget.length) {
            var halfHeight = this.$menu.height() * 0.5;
            var targetCenter = this.scrollTarget.position().top + this.scrollTarget.height() * 0.5;
            var top = targetCenter + this.$menu.scrollTop() - halfHeight;
            this.$menu.scrollTop(top);
        }
    }
  };


  //SELECTORMENU PLUGIN DEFINITION
  $.fn.dropdownmenu = function(option) {
    var args = Array.apply(null, arguments);
    args.shift();
    return this.each(function() {
      var $this = $(this),
        data = $this.data('dropdownmenu'),
        options = typeof option === 'object' && option;

      if (!data) {
        $this.data('dropdownmenu', (data = new DropdownMenu(this, $.extend({}, $.fn.dropdownmenu.defaults, options, $(this).data()))));
      }

      if (typeof option === 'string') {
        data[option].apply(data, args);
      }
    });
  };

  $.fn.dropdownmenu.defaults = {
    activeIndex: false,
    scrollTargetIndex: 0,
    options: ["a", "b", "c"]
  };

  $.fn.dropdownmenu.Constructor = DropdownMenu;

})(jQuery, window, document);
