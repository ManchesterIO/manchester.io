module.exports = function (config) {
    config.set({
        autoWatch: false,
        background: true,
        basePath: '../../',
        browsers: ['PhantomJS'],
        files: [
            'assets/js-test/testMain.js',
            {pattern: 'assets/js/**/*.js', included: false},
            {pattern: 'assets/js-test/**/*.js', included: false},
            {pattern: 'bower_components/**', included: false}
        ],
        frameworks: ['jasmine', 'requirejs'],
        logLevel: config.LOG_WARN,
        reporters: ['progress'],
        singleRun: true
    });
};
