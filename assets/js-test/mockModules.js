define("mockNearbyStationSearch", function() {
    'use strict';

    var NearbyStationSearch = jasmine.createSpy();
    NearbyStationSearch.prototype.init = jasmine.createSpy();

    return NearbyStationSearch;
});
