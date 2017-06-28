'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.default = configureCsp;

var _helmet = require('helmet');

var _helmet2 = _interopRequireDefault(_helmet);

var _uuid = require('uuid');

var _uuid2 = _interopRequireDefault(_uuid);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function configureCsp(app) {
    var devMode = process.env.NODE_ENV !== 'production';

    app.use(function (req, res, next) {
        res.locals.csp_nonce = _uuid2.default.v4();
        next();
    });

    var cspBaseUrls = ["'self'"];
    if (devMode) {
        // Enable live-reloading
        cspBaseUrls = cspBaseUrls.concat(['sandbox.manchester.io:8090', 'ws://sandbox.manchester.io:8090']);
    }
    app.use(_helmet2.default.contentSecurityPolicy({
        directives: {
            defaultSrc: cspBaseUrls,
            scriptSrc: cspBaseUrls.concat([function (req, res) {
                return '\'nonce-' + res.locals.csp_nonce + '\'';
            }]).concat(devMode ? ["'unsafe-eval'"] : []),
            styleSrc: cspBaseUrls.concat(devMode ? ["'unsafe-inline'"] : [])
        }
    }));
};