window.require = {
    baseUrl: 'js',
    paths: {
        'jquery' : 'vendor/jquery',
        'moment': 'vendor/moment',
        'spin': 'vendor/spin'
    },
    shim: {
        'vendor/bootstrap': ['jquery'],
        'vendor/bootstrap-datepicker': ['vendor/bootstrap'],
        'vendor/jquery.dragsort': ['jquery'],
        'vendor/jquery.event.move': ['jquery'],
        'vendor/jquery.event.swipe': ['vendor.event.move'],
        'vendor/jquery.dragsort': ['jquery']
    }
};