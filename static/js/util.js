(function() {

    var util = {};
    
    //See http://stackoverflow.com/questions/2593637/how-to-escape-regular-expression-in-javascript
    util.regex_quote = function(str) {
        return (str+'').replace(/([.?*+^$[\]\\(){}|-])/g, "\\$1");
    };
    



    
    return util;
})();