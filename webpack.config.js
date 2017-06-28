/* eslint-disable comma-dangle */
const fs = require('fs');
const path = require('path');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const ImageminPlugin = require('imagemin-webpack-plugin').default;
const UglifyJSPlugin = require('uglifyjs-webpack-plugin');
const SriPlugin = require('webpack-subresource-integrity');
const OnBuildPlugin = require('on-build-webpack');
const mapValues = require('lodash/mapValues');
const webpack = require('webpack');

try { fs.mkdirSync('build'); } catch (e) {} // eslint-disable-line no-empty
try { fs.mkdirSync('build/test-results'); } catch (e) {} // eslint-disable-line no-empty

const extractSass = new ExtractTextPlugin({
    filename: '[name].css',
    disable: process.env.NODE_ENV !== 'production',
});

const config = {
    entry: {
        bootstrap: [
            'react-hot-loader/patch',
            './frontend/bootstrap.js',
        ],
    },
    output: {
        path: path.resolve(__dirname, 'deploy', 'cookbook', 'manchesterio', 'files', 'default', 'static'),
        filename: '[name].js',
        crossOriginLoading: 'anonymous',
    },
    module: {
        rules: [
            {
                test: /\.jsx?$/,
                exclude: /node_modules/,
                use: [
                    'react-hot-loader/webpack',
                    {
                        loader: 'babel-loader',
                        options: {
                            presets: [
                                [
                                    'env',
                                    {
                                        uglify: true,
                                        modules: false
                                    }
                                ],
                                'react'
                            ],
                        },
                    }
                ],
            },
            {
                test: /\.scss$/,
                use: extractSass.extract({
                    use: [{
                        loader: 'css-loader',
                    }, {
                        loader: 'sass-loader',
                    }],
                    // use style-loader in development
                    fallback: 'style-loader',
                }),
            },
            {
                test: /\.(jpe?g|png|gif|svg)$/,
                loader: 'file-loader?name=[name].[ext]',
            },
        ]
    },
    resolve: {
        extensions: ['.js', '.jsx'],
    },
    plugins: [
        extractSass,
        new webpack.EnvironmentPlugin(['NODE_ENV']),
        new CopyWebpackPlugin([{
            from: 'frontend/images/',
            to: 'images/',
        }]),
        new ImageminPlugin({
            disable: process.env.NODE_ENV !== 'production',
        }),
        new SriPlugin({
            hashFuncNames: ['sha256'],
            enabled: true,
        }),
        new OnBuildPlugin((stats) => {
            fs.writeFileSync(
                path.join(__dirname, 'build', 'sri.json'),
                JSON.stringify(mapValues(stats.compilation.assets, 'integrity'))
            );
        }),
    ],
    watchOptions: {
        aggregateTimeout: 300,
        poll: 200,
    },
    devServer: {
        hot: true,
        host: 'sandbox.manchester.io',
        port: 8090,
    }
};

if (process.env.NODE_ENV === 'production') {
    config.plugins.push(new UglifyJSPlugin());
} else {
    config.plugins.push(new webpack.HotModuleReplacementPlugin());
    config.plugins.push(new webpack.NamedModulesPlugin());
    config.devtool = 'source-map';
}

module.exports = config;
