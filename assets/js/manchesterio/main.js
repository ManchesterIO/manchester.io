define(['manchesterio/nearbyStationSearch'], function(NearbyStationSearch) {

    function init(canvas) {
        var nearbyStationSearch = new NearbyStationSearch(canvas.querySelector('.nearby-station-search'));
        nearbyStationSearch.init();
    }

    return init;
});
