// @flow

import bunyan from 'bunyan';

export default bunyan.createLogger({
    name: 'manchesterio',
    serializers: bunyan.stdSerializers,
    level: process.env.NODE_ENV === 'production' ? 'warn' : 'info',
});
