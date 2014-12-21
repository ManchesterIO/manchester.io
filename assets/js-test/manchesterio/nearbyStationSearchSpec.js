define(['manchesterio/nearbyStationSearch'], function(NearbyStationSearch) {
    "use strict";

    describe("the nearby stations button", function() {

        var nearbyStationSearch, button, status, template = '/example/{lat},{lon}';

        beforeEach(function() {
            button = document.createElement('button');
            button.dataset.href = template;
            status = document.createElement('h2');
            button.appendChild(status);
            status.classList.add('nearby-station-search__status');

            if (navigator.geolocation === undefined) {
                navigator.geolocation = { getCurrentPosition: function() { } };
            }
            spyOn(navigator.geolocation, 'getCurrentPosition');

            nearbyStationSearch = new NearbyStationSearch(button);
        });

        it("should enable the button on init", function() {
            button.disabled = true;

            nearbyStationSearch.init();

            expect(button.disabled).toBeFalsy();
        });

        it("should change the status text on click", function() {
            nearbyStationSearch.init();

            button.click();

            expect(status.textContent).toBe("Determining your location");
        });

        it("should change the status text on error", function() {
            nearbyStationSearch.init();

            button.click();
            geolocationError(1);

            expect(status.textContent).toBe("Your location could not be determined");
        });

        it("should redirect on success", function() {
            nearbyStationSearch.init();

            spyOn(nearbyStationSearch, '_redirect');
            button.click();
            geolocationSuccess(54.6, 1.23);

            expect(nearbyStationSearch._redirect).toHaveBeenCalledWith('/example/54.6,1.23');
        });

        function geolocationSuccess(lat, lon) {
            navigator.geolocation.getCurrentPosition.calls.mostRecent().args[0](
                {coords: {latitude: lat, longitude: lon}}
            );
        }

        function geolocationError(code) {
            navigator.geolocation.getCurrentPosition.calls.mostRecent().args[1]({code: code});
        }
    });

});
