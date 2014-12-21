define(['polyfills/bind'], function() {
    'use strict';

    function roundCoords(coords) {
        return {
            latitude: Math.round(coords.latitude * 100000) / 100000,
            longitude: Math.round(coords.longitude * 100000) / 100000
        };
    }

    var NearbyStationSearch = function(button) {
        this._button = button;
        this._statusText = button.querySelector('.nearby-station-search__status');
    };

    NearbyStationSearch.prototype.init = function() {
        this._button.disabled = false;
        this._button.addEventListener('click', this._click.bind(this), false);
    };

    NearbyStationSearch.prototype._click = function() {
        this._statusText.textContent = 'Determining your location';
        navigator.geolocation.getCurrentPosition(
            this._geolocationSuccess.bind(this),
            this._geolocationError.bind(this)
        );
    };

    NearbyStationSearch.prototype._geolocationSuccess = function(position) {
        var coords = roundCoords(position.coords);
        var redirectUrl = this._button.dataset.href
            .replace('{lat}', coords.latitude)
            .replace('{lon}', coords.longitude);
        this._redirect(redirectUrl);
    };

    NearbyStationSearch.prototype._geolocationError = function() {
        this._statusText.textContent = 'Your location could not be determined';
    };

    NearbyStationSearch.prototype._redirect = function(path) {
        window.location.pathname = path;
    };

    return NearbyStationSearch;

});
