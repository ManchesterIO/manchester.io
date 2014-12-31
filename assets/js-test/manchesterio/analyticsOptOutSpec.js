define(['manchesterio/analyticsOptOut', 'cookies'], function(AnalyticsOptOut, cookies) {
    'use strict';

    describe("analytics opt out", function() {

        var analyticsOptOut,
            analyticsBanner,
            optOutButton;

        beforeEach(function() {
            analyticsBanner = document.createElement('div');
            optOutButton = document.createElement('button');
            optOutButton.classList.add('analytics-opt-out__action');
            analyticsBanner.appendChild(optOutButton);
            analyticsOptOut = new AnalyticsOptOut(analyticsBanner);
            cookies.expire('analytics_opt_out');
            window['ga-disable-UA-1234-1'] = undefined;
        });

        it("shows the banner when the user has not yet made a choice", function() {
            analyticsOptOut.init();

            expect(analyticsBanner.classList.contains('first-run')).toBeTruthy();
        });

        it("removes the banner when the user makes a choice", function() {
            analyticsOptOut.init();

            optOutButton.click();

            expect(analyticsBanner.classList.contains('first-run')).toBeFalsy();
        });

        it("does not show the banner when the user has already seen it", function() {
            cookies.set('analytics_opt_out', 'true');

            analyticsOptOut.init();

            expect(analyticsBanner.classList.contains('first-run')).toBeFalsy();
        });

        it("defaults to be not opted out", function() {
            analyticsOptOut.init();

            expect(cookies.get('analytics_opt_out')).toBe('false');
        });

        it("opts you out when you click the opt out button", function() {
            analyticsOptOut.init();

            optOutButton.click();

            expect(cookies.get('analytics_opt_out')).toBe('true');
        });

        it("disables Google Analytics when the user has opted out", function() {
            cookies.set('analytics_opt_out', 'true');

            analyticsOptOut.init();

            expect(window['ga-disable-UA-1234-1']).toBeTruthy();
        });

    });

});
