// @flow

import express from 'express';
import handlebars from 'express-handlebars';
import helmet from 'helmet';
import configureCsp from './csp';
import indexController from './controllers/index';

const app = express();

app.engine('handlebars', handlebars({
    defaultLayout: 'main',
    layoutsDir: 'api/views/layouts/',
    partialsDir: 'api/views/partials/',
}));
app.set('view engine', 'handlebars');
app.set('views', 'api/views');
if (process.env.NODE_ENV === 'production') {
    app.enable('view cache');
}

app.disable('x-powered-by');
app.use(helmet.frameguard({ action: 'deny' }));
configureCsp(app);

app.get('/', indexController);

export default app;
