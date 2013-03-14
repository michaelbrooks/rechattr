$(document).ready(function() {
    var app = rechattr.js_app;
    if (app in rechattr.classes) {
        app = rechattr.classes[app];
        new app();
    }
});