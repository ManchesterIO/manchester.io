define(['leaflet'], function(L) {
    // Used from: http://charliecroom.com/index.php/web/numbered-markers-in-leaflet

    L.NumberedIcon = L.Icon.extend({
        options: {
            iconUrl: 'http://www.charliecroom.com/marker_hole.png',
            number: '',
            shadowUrl: null,
            iconSize: new L.Point(25, 41),
            iconAnchor: new L.Point(13, 41),
            popupAnchor: new L.Point(0, -33),
            className: 'leaflet-div-icon'
        },

        createIcon: function () {
            var div = document.createElement('div');
            var img = this._createImg(this.options.iconUrl);
            var numdiv = document.createElement('div');
            numdiv.setAttribute("class", "number");
            numdiv.innerHTML = this.options.number || '';
            div.appendChild(img);
            div.appendChild(numdiv);
            this._setIconStyles(div, 'icon');
            return div;
        },

        createShadow: function () {
            return null;
        }
    });

    L.numberedIcon = function(options) {
        return new L.NumberedIcon(options);
    };

});
