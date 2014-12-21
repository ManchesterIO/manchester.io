define(['leaflet', 'contrib/leaflet.numbered_markers'], function(L) {

    var mapIdCounter = 1;

    var SearchResults = function(mapCanvas, resultNodes) {
        this._mapCanvas = mapCanvas;
        this._resultNodes = resultNodes;
    };

    SearchResults.prototype.init = function() {
        var mapDiv = document.createElement('div');
        mapDiv.classList.add('map');
        mapDiv.id = 'map' + mapIdCounter;

        this._mapCanvas.appendChild(mapDiv);
        this._map = L.map(mapDiv.id);
        L.tileLayer(
            'http://otile{s}.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.jpeg',
            {
                attribution: 'Tiles by <a href="http://www.mapquest.com/">MapQuest</a> &mdash; Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
                subdomains: '1234'
            }
        ).addTo(this._map);

        var currentLatLon = [parseFloat(this._mapCanvas.dataset.startingLat), parseFloat(this._mapCanvas.dataset.startingLon)];
        L.marker(currentLatLon).addTo(this._map);

        var latLons = [currentLatLon];

        for (var i = 0; i < this._resultNodes.length; ++i) {
            var latLon = [parseFloat(this._resultNodes[i].dataset.lat), parseFloat(this._resultNodes[i].dataset.lon)];
            latLons.push(latLon);
            L.marker(latLon, { icon: L.numberedIcon({number: i + 1}) }).addTo(this._map);
        }

        this._map.fitBounds(latLons, { padding: [32, 32] });
    };

    return SearchResults;
});
