define(['manchesterio/nearbyStationSearch', 'manchesterio/searchResults'], function(NearbyStationSearch, SearchResults) {

    var canvas;

    function init(_canvas) {
        canvas = _canvas;
        initNearbyStationSearch();
        SearchResults();
    }

    function initNearbyStationSearch() {
        var searchButton = canvas.querySelector('.nearby-station-search');
        if (searchButton) {
            var nearbyStationSearch = new NearbyStationSearch();
            nearbyStationSearch.init();
        }
    }

    return init;
});
