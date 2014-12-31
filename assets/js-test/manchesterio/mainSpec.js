require.config({
   map: {
       "manchesterio/main": {
           'contrib/google-analytics': 'mockGoogleAnalytics',
           "manchesterio/nearbyStationSearch": "mockNearbyStationSearch",
           "manchesterio/searchResults": "mockSearchResults"
       }
   }
});

define(
    ['manchesterio/main', 'mockNearbyStationSearch', 'mockSearchResults', 'mockGoogleAnalytics'],
    function(main, mockNearbyStationSearch, mockSearchResults, mockGA) {

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

        it("initialises the search result map", function() {
            var mapCanvas = document.createElement('div'),
                searchResults = [],
                i;
            mapCanvas.classList.add('results-map');
            canvas.appendChild(mapCanvas);

            for (i = 0; i < 5; ++i) {
                var searchResult = document.createElement('div');
                searchResult.classList.add('search-result');
                canvas.appendChild(searchResult);
                searchResults.push(searchResult);
            }

            main(canvas);

            expect(mockSearchResults).toHaveBeenCalled();
            expect(mockSearchResults.calls.mostRecent().args[0]).toBe(mapCanvas);
            for (i = 0; i < 5; ++i) {
                expect(mockSearchResults.calls.mostRecent().args[1][i]).toBe(searchResults[i]);
            }

            expect(mockSearchResults.prototype.init).toHaveBeenCalled();
        });

        it("initialises Google Analytics", function() {
            main(canvas);

            expect(mockGA).toHaveBeenCalledWith('create', 'UA-427161-9', 'auto');
            expect(mockGA).toHaveBeenCalledWith('send', 'pageview');
        });

    });

});
