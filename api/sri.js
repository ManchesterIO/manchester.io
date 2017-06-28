// @flow

import fs from 'fs';
import path from 'path';

module.exports = function loadSri() {
    let sriHashes;
    if (process.env.NODE_ENV === 'production') {
        // eslint-disable-next-line global-require
        sriHashes = require('../build/sri.json');
    } else {
        // eslint-disable-next-line no-sync
        sriHashes = JSON.parse(
            fs.readFileSync(path.join(__dirname, '..', 'build', 'sri.json'), 'utf8'),
        );
    }

    const escapedSriHashes = {};
    Object.keys(sriHashes).forEach((filename) => {
        escapedSriHashes[filename.replace('.', '_')] = sriHashes[filename];
    });

    return escapedSriHashes;
};
