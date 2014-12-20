define(['manchesterio/nearbyStationSearch'], function(NearbyStationSearch) {
    "use strict";

    describe("the nearby stations button", function() {

        var nearbyStationSearch, button;

        beforeEach(function() {
            button = document.createElement('button');
            nearbyStationSearch = new NearbyStationSearch(button);
        });

        it("should enable the button on init", function() {
            button.disabled = true;

            nearbyStationSearch.init();

            expect(button.disabled).toBeFalsy();
        });
    });

});
