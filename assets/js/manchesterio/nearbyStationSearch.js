define(function() {

    NearbyStationSearch = function(button) {
        this.button = button;
    };

    NearbyStationSearch.prototype.init = function() {
        this.button.disabled = false;
    };

    return NearbyStationSearch;
});
