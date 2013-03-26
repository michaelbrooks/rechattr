$(document).ready(function() {
    var app = rechattr.config.app_name;
    if (app in rechattr.classes) {
        app = rechattr.classes[app];
        new app();
    }
});