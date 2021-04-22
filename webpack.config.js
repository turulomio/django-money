const path = require('path');

// webpack.config.js

module.exports = {
  entry: './money/static/index.js',  // path to our input file
  output: {
    filename: 'vue-bundle.js',  // output bundle file name
    path: path.resolve(__dirname, './money/static/js/'),  // path to our Django static directory
  },

-ww
  module: {
    rules: [
      {
        test: /\.s(c|a)ss$/,
        use: [
          'vue-style-loader',
          'css-loader',
          {
            loader: 'sass-loader',
            // Requires sass-loader@^7.0.0
            options: {
              implementation: require('sass'),
              indentedSyntax: true // optional
            },
            // Requires >= sass-loader@^8.0.0
            options: {
              implementation: require('sass'),
              sassOptions: {
                indentedSyntax: true // optional
              },
            },
          },
        ],
      },
    ],
  }
}



