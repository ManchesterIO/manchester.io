// @flow

import helmet from 'helmet';
import uuid from 'uuid';

export default function configureCsp(app) {
    const devMode = process.env.NODE_ENV !== 'production';

    app.use((req, res, next) => {
        res.locals.csp_nonce = uuid.v4();
        next();
    });

    let cspBaseUrls = ["'self'"];
    if (devMode) {
        // Enable live-reloading
        cspBaseUrls = cspBaseUrls.concat([
            'sandbox.manchester.io:8090',
            'ws://sandbox.manchester.io:8090',
        ]);
    }
    app.use(helmet.contentSecurityPolicy({
        directives: {
            defaultSrc: cspBaseUrls,
            scriptSrc: cspBaseUrls.concat([
                (req, res) => `'nonce-${res.locals.csp_nonce}'`,
            ]).concat(devMode ? ["'unsafe-eval'"] : []),
            styleSrc: cspBaseUrls.concat(devMode ? ["'unsafe-inline'"] : []),
        },
    }));
};
