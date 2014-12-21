require.config({
    map: {
        "manchesterio/searchResults": {
            "leaflet": "mockLeaflet"
        }
    }
});

define(['manchesterio/searchResults', 'mockLeaflet'], function(SearchResults, mockLeaflet) {
    "use strict";

    describe("the search results", function() {

        var searchResults, mapCanvas, results;

        beforeEach(function() {
            mapCanvas = document.createElement('div');
            mapCanvas.dataset.startingLat = '1.23';
            mapCanvas.dataset.startingLon = '4.56';
            results = [];

            searchResults = new SearchResults(mapCanvas, results);
        });

        it("creates a div with an ID for leaflet to render into", function() {
            searchResults.init();

            var mapDiv = mapCanvas.querySelector('div');

            expect(mapDiv.classList.contains('map')).toBeTruthy();
            expect(mapDiv.id).not.toBeFalsy();
        });

        it("initialises Leaflet with the div", function() {
            searchResults.init();

            var mapDiv = mapCanvas.querySelector('div');

            expect(mockLeaflet.map).toHaveBeenCalledWith(mapDiv.id);
            expect(mockLeaflet.tileLayer).toHaveBeenCalledWith(
                'http://otile{s}.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.jpeg',
                {
                    attribution: 'Tiles by <a href="http://www.mapquest.com/">MapQuest</a> &mdash; Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
                    subdomains: '1234'
                }
            );
            expect(mockLeaflet.mockTileLayer.addTo).toHaveBeenCalledWith(mockLeaflet.mockMap);
        });

        it("sets the view around the appropriate location", function() {
            searchResults.init();

            expect(mockLeaflet.mockMap.setView).toHaveBeenCalledWith([1.23, 4.56], 15);
        });

        it('creates a marker for each search result', function() {
            var result = document.createElement('div');
            result.dataset.lat = '1.23';
            result.dataset.lon = '4.56';
            results.push(result);

            searchResults.init();

            expect(mockLeaflet.marker).toHaveBeenCalledWith([1.23, 4.56]);
            expect(mockLeaflet.mockMarker.addTo).toHaveBeenCalledWith(mockLeaflet.mockMap);
        });

    });

});
