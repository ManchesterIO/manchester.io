define(function() {

    window.GoogleAnalyticsObject = "ga";
    window.ga = function () { (window.ga.q = window.ga.q || []).push(arguments); };
    window.ga.l = 1 * new Date();

    require(["//www.google-analytics.com/analytics.js"]);

    return function () { window.ga.apply(this, arguments); };

});
