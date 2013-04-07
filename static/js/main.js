$(document).ready(function() {
    //Turn off []-appending to posted arrays
    //More: http://forum.jquery.com/topic/jquery-post-1-4-1-is-appending-to-vars-when-posting-from-array-within-array
    $.ajaxSettings.traditional = true;
    
    var app = rechattr.config.app_name;
    if (app in rechattr.classes) {
        app = rechattr.classes[app];
        new app();
    }
});