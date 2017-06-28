// @flow

import cluster from 'cluster';
import app from './app';
import logger from './logger';

if (cluster.isMaster) {
    const cpuCount = require('os').cpus().length; // eslint-disable-line global-require
    for (let i = 0; i < cpuCount; i += 1) {
        cluster.fork();
    }
} else {
    app.listen(8080, () => {
        logger.info('Server started');
    });
}
