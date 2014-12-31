define(['manchesterio/nearbyStationSearch', 'manchesterio/searchResults', 'contrib/google-analytics'],
    function(NearbyStationSearch, SearchResults, ga) {

    var canvas;

    function init(_canvas) {
        canvas = _canvas;
        initNearbyStationSearch();
        initSearchResults();
        initGoogleAnalytics();
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

    function initGoogleAnalytics() {
        ga('create', 'UA-427161-9', 'auto');
        ga('send', 'pageview');
    }

    return init;
});
