define(['leaflet', 'contrib/leaflet.numbered_markers'], function(L) {

    var mapIdCounter = 1;

    var SearchResults = function(mapCanvas, resultNodes) {
        this._mapCanvas = mapCanvas;
        this._resultNodes = resultNodes;
        this._latLons = [];
    };

    SearchResults.prototype.init = function() {
        this._initLeaflet();
        this._initHomeMarker();
        this._initResultMarkers();

        this._map.fitBounds(this._latLons, { padding: [32, 32] });
    };

    SearchResults.prototype._initLeaflet = function() {
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
    };

    SearchResults.prototype._initHomeMarker = function() {
        var currentLatLon = [parseFloat(this._mapCanvas.dataset.startingLat), parseFloat(this._mapCanvas.dataset.startingLon)];
        L.marker(currentLatLon).addTo(this._map);
        this._latLons.push(currentLatLon);
    };

    SearchResults.prototype._initResultMarkers = function() {
        for (var i = 0; i < this._resultNodes.length; ++i) {
            this._initResultMarker(this._resultNodes[i], i + 1);
        }
    };

    SearchResults.prototype._initResultMarker = function(resultNode, index) {
        var latLon = [parseFloat(resultNode.dataset.lat), parseFloat(resultNode.dataset.lon)];
        this._latLons.push(latLon);

        var marker = L.marker(latLon, { icon: L.numberedIcon({number: index}) });
        marker.addTo(this._map);

        marker.bindPopup(resultNode.querySelector('.search-result__title').textContent);
        this._bindOpenPopup(resultNode, marker);
        this._bindClosePopup(resultNode, marker);
    };

    SearchResults.prototype._bindOpenPopup = function(node, marker) {
        node.addEventListener('mouseover', function() {
            marker.openPopup();
        }, false);
    };

    SearchResults.prototype._bindClosePopup = function(node, marker) {
        node.addEventListener('mouseout', function(ev) {
            if (ev.target === node && (ev.relatedTarget === null || ev.relatedTarget.parentNode.parentNode !== node)) {
                marker.closePopup();
            }
        }, false);
    };

    return SearchResults;
});
