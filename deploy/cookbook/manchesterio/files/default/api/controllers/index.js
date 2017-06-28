'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _sri = require('../sri');

var _sri2 = _interopRequireDefault(_sri);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

exports.default = function (req, res) {
    var sriHashes = (0, _sri2.default)();
    res.render('index', {
        page_title: 'Hello',
        csp_nonce: res.locals.csp_nonce,
        sri: {
            js: sriHashes['static/bootstrap_js'],
            css: sriHashes['static/bootstrap_css']
        }
    });
};