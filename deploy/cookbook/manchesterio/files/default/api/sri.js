'use strict';

var _fs = require('fs');

var _fs2 = _interopRequireDefault(_fs);

var _path = require('path');

var _path2 = _interopRequireDefault(_path);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

module.exports = function loadSri() {
    var sriHashes = void 0;
    if (process.env.NODE_ENV === 'production') {
        // eslint-disable-next-line global-require
        sriHashes = require('../build/sri.json');
    } else {
        // eslint-disable-next-line no-sync
        sriHashes = JSON.parse(_fs2.default.readFileSync(_path2.default.join(__dirname, '..', 'build', 'sri.json'), 'utf8'));
    }

    var escapedSriHashes = {};
    Object.keys(sriHashes).forEach(function (filename) {
        escapedSriHashes[filename.replace('.', '_')] = sriHashes[filename];
    });

    return escapedSriHashes;
};