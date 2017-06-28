// @flow

import type { $Request, $Response } from 'express';

import loadSri from '../sri';

export default (req: $Request, res: $Response) => {
    const sriHashes = loadSri();
    res.render('index', {
        page_title: 'Hello',
        csp_nonce: res.locals.csp_nonce,
        sri: {
            js: sriHashes['static/bootstrap_js'],
            css: sriHashes['static/bootstrap_css'],
        },
    });
};
