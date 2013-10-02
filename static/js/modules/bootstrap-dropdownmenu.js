define(['jquery'], function ($) {

    'use strict';

    // DropdownMenu PUBLIC CLASS DEFINITION
    var DropdownMenu = function (element, options) {
        this.choices = options.choices;
        this.selectedItem = options.selected;
        this.display = options.display;

        this.$element = $(element);
        this._init();
    };

    DropdownMenu.prototype = {

        constructor: DropdownMenu,

        _init: function () {
            var self = this;

            this.$toggle = this.$element.is('.dropdown-toggle') ? this.$element : this.$element.find('.dropdown-toggle');
            if (this.$toggle.length) {
                throw 'Could not find a .dropdown-toggle element';
            }

            this.$dropdown = this.$element.is('.dropdown') ? this.$element : this.$element.parents('.dropdown');
            if (this.$dropdown.length === 0) {
                throw 'DropdownMenu must be created inside of a .dropdown element';
            }

            //Construct the menu itself
            this.buildMenu();
        },

        menu: function (choices) {
            this.choices = choices;
            this.selectedChoice = null;
            this.selectedItem = null;
            this.buildMenu();
        },

        buildMenu: function () {
            var self = this;

            if (!this.$menu) {
                this.$menu = $('<ul class="dropdown-menu">');
                this.$element.prepend(this.$menu);
            } else {
                this.$menu.empty();
            }

            if (this.choices) {
                $.each(this.choices, function (index, item) {
                    var display = self.display(item);
                    if (display) {
                        var choice = $('<li><a tabindex="-1" href="#">' + (display) + '</a></li>');
                        if (item === self.selectedItem) {
                            choice.addClass('active');
                            self.selectedChoice = choice;
                        }

                        self.$menu.append(choice);

                        choice.on('click', function (event) {
                            self.$element.trigger('dropdown.select', item);
                            event.preventDefault();
                            return false;
                        });
                    }
                });
            }
        },

        update: function (item) {
            var self = this;
            $.each(this.choices, function (index, value) {
                if (value === item) {
                    var choices = self.$menu.children();
                    choices.removeClass('active');

                    self.selectedChoice = $(choices[index]);
                    self.selectedChoice.addClass('active');
                    self.selectedItem = item;
                    return false;
                }
            });

        },

        scrollToSelected: function () {
            if (this.selectedChoice && this.selectedChoice.length) {
                var halfHeight = this.$menu.height() * 0.5;
                var targetCenter = this.selectedChoice.position().top + this.selectedChoice.height() * 0.5;
                var top = targetCenter + this.$menu.scrollTop() - halfHeight;
                this.$menu.scrollTop(top);
            }
        },

        hide: function () {
            this.$element.removeClass('open');
        },

        show: function () {
            this.buildMenu();
            this.$element.addClass('open');
            this.scrollToSelected();
        }
    };


    //SELECTORMENU PLUGIN DEFINITION
    $.fn.dropdownmenu = function (option) {
        var args = Array.apply(null, arguments);
        args.shift();
        return this.each(function () {
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

    return $;
});
