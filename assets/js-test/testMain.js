(function() {
    "use strict";

    var tests = [];

    for (var file in window.__karma__.files) {
        if (window.__karma__.files.hasOwnProperty(file)) {
            if (/Spec\.js$/.test(file)) {
                tests.push(file);
            }
        }
    }

    requirejs.config({
        baseUrl: '/base/assets/js',
        deps: tests,
        callback: window.__karma__.start
    });

})();
