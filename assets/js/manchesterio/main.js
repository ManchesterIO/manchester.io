define(['manchesterio/nearbyStationSearch', 'manchesterio/searchResults'], function(NearbyStationSearch, SearchResults) {

    var canvas;

    function init(_canvas) {
        canvas = _canvas;
        initNearbyStationSearch();
        initSearchResults();
    }

    function initNearbyStationSearch() {
        var searchButton = canvas.querySelector('.nearby-station-search');
        if (searchButton) {
            var nearbyStationSearch = new NearbyStationSearch(searchButton);
            nearbyStationSearch.init();
        }
    }

    function initSearchResults() {
        var searchMap = canvas.querySelector('.results-map'),
            searchResultItems = canvas.querySelectorAll('.search-result');

        if (searchMap) {
            var searchResults = new SearchResults(searchMap, searchResultItems);
            searchResults.init();
        }

    }

    return init;
});
