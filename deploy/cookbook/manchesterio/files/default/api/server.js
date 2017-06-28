'use strict';

var _cluster = require('cluster');

var _cluster2 = _interopRequireDefault(_cluster);

var _app = require('./app');

var _app2 = _interopRequireDefault(_app);

var _logger = require('./logger');

var _logger2 = _interopRequireDefault(_logger);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

if (_cluster2.default.isMaster) {
    var cpuCount = require('os').cpus().length; // eslint-disable-line global-require
    for (var i = 0; i < cpuCount; i += 1) {
        _cluster2.default.fork();
    }
} else {
    _app2.default.listen(8080, function () {
        _logger2.default.info('Server started');
    });
}