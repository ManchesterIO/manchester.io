require.config({
    map: {
        "manchesterio/searchResults": {
            "leaflet": "mockLeaflet",
            'contrib/leaflet.numbered_markers': 'mockLeaflet'
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

        it("creates a marker for the current position", function() {
            searchResults.init();

            expect(mockLeaflet.marker).toHaveBeenCalledWith([1.23, 4.56]);
            expect(mockLeaflet.mockMarker.addTo).toHaveBeenCalledWith(mockLeaflet.mockMap);
        });

        it('creates a marker for each search result', function() {
            fakeResult();

            searchResults.init();

            expect(mockLeaflet.marker).toHaveBeenCalledWith([7.89, 10.1112], { icon: mockLeaflet.mockIcon });
            expect(mockLeaflet.numberedIcon).toHaveBeenCalledWith({number: 1});
            expect(mockLeaflet.mockMarker.addTo).toHaveBeenCalledWith(mockLeaflet.mockMap);
        });

        it("sets the map to fit all the markers on there", function() {
            fakeResult();

            searchResults.init();

            expect(mockLeaflet.mockMap.fitBounds).toHaveBeenCalledWith(
                [[1.23, 4.56], [7.89, 10.1112]], { padding: [32, 32] }
            );
        });

        it('adds a popup with the station name', function() {
            fakeResult();

            searchResults.init();

            expect(mockLeaflet.mockMarker.bindPopup).toHaveBeenCalledWith('Trumpton Station');
        });

        it('pops up the title on hover', function() {
            var result = fakeResult();

            searchResults.init();
            var event = document.createEvent('MouseEvents');
            event.initMouseEvent('mouseover');
            result.dispatchEvent(event);

            expect(mockLeaflet.mockMarker.openPopup).toHaveBeenCalled();
        });

        it('closes the popup when the mouse leaves', function() {
            var result = fakeResult();

            searchResults.init();
            var event = document.createEvent('MouseEvents');
            event.initMouseEvent('mouseout');
            result.dispatchEvent(event);

            expect(mockLeaflet.mockMarker.closePopup).toHaveBeenCalled();
        });

        function fakeResult() {
            var result = document.createElement('div');
            result.dataset.lat = '7.89';
            result.dataset.lon = '10.1112';
            var title = document.createElement('h2');
            title.classList.add('search-result__title');
            title.textContent = 'Trumpton Station';
            result.appendChild(title);
            results.push(result);
            return result;
        }

    });

});
