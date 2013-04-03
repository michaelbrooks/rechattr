;(function($, window, document, undefined) {

  'use strict'; // jshint ;_;

  // DropdownMenu PUBLIC CLASS DEFINITION
  var DropdownMenu = function(element, options) {
    this.choices = options.choices;
    this.selectedKey = options.selectedKey;
    this.display = options.display;
    this.key = options.key;
    
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
    },
    
    updateMenu: function() {
        var self = this;
        
        if (!this.$menu) {
            return;
        }
        
        var menuChoices = this.$menu.children();
        $.each(this.choices, function(index, item) {
            var choice = $(menuChoices[index]);
            var display = self.display(item);
            
            if (!display) {
                //Hide items with no display
                choice.hide();
            } else {
                choice.show();
            }
            
            choice.html('<a tabindex="-1" href="#">' + (display) + '</a>');
        });
    },
    
    buildMenu: function() {
        var self = this;
        
        if (!this.$menu) {
            this.$menu = $('<ul class="dropdown-menu">');
            this.$element.prepend(this.$menu);
        } else {
            this.$menu.empty();
        }
        
        $.each(this.choices, function(index, item) {
            var display = self.display(item);
            var choice = $('<li><a tabindex="-1" href="#">' + (display) + '</a></li>');
            self.$menu.append(choice);
            
            choice.on('click', function(event) {
                self.$element.trigger('dropdown.select', item);
            });
        });
    },
    
    update: function(itemKey) {
        var self = this;
        $.each(this.choices, function(index, value) {
            if (self.key(value) == itemKey) {
                var choices = self.$menu.children();
                choices.removeClass('active');
                
                self.selectedChoice = $(choices[index]);
                self.selectedChoice.addClass('active');
                self.selectedKey = itemKey;
                return false;
            }
        });
        
    },
    
    scrollToSelected: function() {
        if (this.selectedChoice && this.selectedChoice.length) {
            var halfHeight = this.$menu.height() * 0.5;
            var targetCenter = this.selectedChoice.position().top + this.selectedChoice.height() * 0.5;
            var top = targetCenter + this.$menu.scrollTop() - halfHeight;
            this.$menu.scrollTop(top);
        }
    },
    
    hide: function() {
        this.$element.removeClass('open');
    },
    
    show: function() {
        this.$element.addClass('open');
        
        this.updateMenu()
        this.scrollToSelected();
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
