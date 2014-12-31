define(['cookies'], function(cookies) {
    'use strict';

    var cookieName = 'analytics_opt_out';

    var setOptOutCookie = function(value) {
        cookies.set(cookieName, value, { expires: 60 * 60 * 24 * 365 * 10 });
    };

    var AnalyticsOptOut = function(analyticsBanner) {
        this._analyticsBanner = analyticsBanner;
        this._optOutButton = analyticsBanner.querySelector('.analytics-opt-out__action');
    };

    AnalyticsOptOut.prototype.init = function() {
        if (cookies.get(cookieName) === undefined) {
            this._analyticsBanner.classList.add('first-run');
            setOptOutCookie('false');
        } else if (cookies.get(cookieName) === 'true') {
            window['ga-disable-UA-1234-1'] = true;
        }

        this._optOutButton.addEventListener('click', this._optOut.bind(this));
    };

    AnalyticsOptOut.prototype._optOut = function() {
        setOptOutCookie('true');
        this._analyticsBanner.classList.remove('first-run');
    };

    return AnalyticsOptOut;

});
