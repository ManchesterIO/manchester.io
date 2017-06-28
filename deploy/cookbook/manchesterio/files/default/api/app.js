'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _express = require('express');

var _express2 = _interopRequireDefault(_express);

var _expressHandlebars = require('express-handlebars');

var _expressHandlebars2 = _interopRequireDefault(_expressHandlebars);

var _helmet = require('helmet');

var _helmet2 = _interopRequireDefault(_helmet);

var _csp = require('./csp');

var _csp2 = _interopRequireDefault(_csp);

var _index = require('./controllers/index');

var _index2 = _interopRequireDefault(_index);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var app = (0, _express2.default)();

app.engine('handlebars', (0, _expressHandlebars2.default)({
    defaultLayout: 'main',
    layoutsDir: 'api/views/layouts/',
    partialsDir: 'api/views/partials/'
}));
app.set('view engine', 'handlebars');
app.set('views', 'api/views');
if (process.env.NODE_ENV === 'production') {
    app.enable('view cache');
}

app.disable('x-powered-by');
app.use(_helmet2.default.frameguard({ action: 'deny' }));
(0, _csp2.default)(app);

app.get('/', _index2.default);

exports.default = app;