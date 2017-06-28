module.exports = {
    "env": {
        "node": true,
        "browser": true,
        "mocha": true,
        "jasmine": true,
        "es6": true
    },
    "parser": "babel-eslint",
    "plugins": [
        "babel",
        "flowtype",
        "react"
    ],
    "extends": [
        "airbnb",
        "plugin:flowtype/recommended"
    ],
    "rules": {
        "indent": [2, 4],
    },
};
