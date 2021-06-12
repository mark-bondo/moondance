const BundleTracker = require("webpack-bundle-tracker");

const pages = {
    "kpi-dashboard": {
        entry: './src/vue_app_configs.js',
        chunks: ['chunk-vendors']
    }
}

module.exports = {
    pages: pages,
    filenameHashing: false,
    productionSourceMap: false,
    publicPath: process.env.NODE_ENV === 'production' ?
        '' : 'http://127.0.0.1:8080',
    outputDir: '../moondance/static/vue/',

    chainWebpack: config => {
        config.optimization
            .splitChunks({
                cacheGroups: {
                    vendor: {
                        test: /[\\/]node_modules[\\/]/,
                        name: "chunk-vendors",
                        chunks: "all",
                        priority: 1
                    },
                },
            });

        Object.keys(pages).forEach(page => {
            config.plugins.delete(`html-${page}`);
            config.plugins.delete(`preload-${page}`);
            config.plugins.delete(`prefetch-${page}`);
        })

        config.plugin('BundleTracker').use(BundleTracker, [{
            filename: '../vue_frontend/webpack-stats.json'
        }]);

        config.resolve.alias
            .set('__STATIC__', 'static')

        config.devServer
            .public('http://127.0.0.1:8080')
            .host('127.0.0.1')
            .port(8080)
            .hotOnly(true)
            .watchOptions({
                poll: 1000
            })
            .https(false)
            .headers({
                "Access-Control-Allow-Origin": ["*"]
            })

    },
    transpileDependencies: ['vuetify']
};
