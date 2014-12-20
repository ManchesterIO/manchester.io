require.config({
   map: {
       "manchesterio/main": {
           "manchesterio/nearbyStationSearch": "mockNearbyStationSearch"
       }
   }
});

define(['manchesterio/main', 'mockNearbyStationSearch'], function(main, mockNearbyStationSearch) {
    "use strict";

    var canvas;

    beforeEach(function() {
        canvas = document.createElement('div');
    });

    describe("page initialisation", function() {
        it("initialises the nearby search buttons", function() {
            var button = document.createElement('button');
            button.classList.add('nearby-station-search');
            canvas.appendChild(button);

            main(canvas);

            expect(mockNearbyStationSearch.prototype.init).toHaveBeenCalled();
        });
    });

});
