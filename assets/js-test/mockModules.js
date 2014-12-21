define("mockNearbyStationSearch", function() {
    'use strict';

    var NearbyStationSearch = jasmine.createSpy();
    NearbyStationSearch.prototype.init = jasmine.createSpy();

    return NearbyStationSearch;
});

define("mockSearchResults", function() {
    'use strict';

    var SearchResults = jasmine.createSpy();
    SearchResults.prototype.init = jasmine.createSpy();

    return SearchResults;
});


define('mockLeaflet', function() {
    'use strict';

    var mockMap = {
        fitBounds: jasmine.createSpy(),
        setView: jasmine.createSpy()
    };

    var mockMarker = {
        addTo: jasmine.createSpy(),
        bindPopup: jasmine.createSpy(),
        closePopup: jasmine.createSpy(),
        openPopup: jasmine.createSpy()
    };

    var mockIcon = { };

    var mockTileLayer = {
        addTo: jasmine.createSpy()
    };

    var L = {
        map: jasmine.createSpy(),
        mockMap: mockMap,

        marker: jasmine.createSpy(),
        mockMarker: mockMarker,

        numberedIcon: jasmine.createSpy(),
        mockIcon: mockIcon,

        tileLayer: jasmine.createSpy(),
        mockTileLayer: mockTileLayer
    };

    L.map.and.returnValue(mockMap);
    L.marker.and.returnValue(mockMarker);
    L.numberedIcon.and.returnValue(mockIcon);
    L.tileLayer.and.returnValue(mockTileLayer);

    return L;
});
