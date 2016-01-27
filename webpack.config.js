module.exports = {
  entry: __dirname + '/client/jsx/application.jsx',
  output: {
    path: __dirname + '/src/sgd/backend/static/js/',
    filename: 'application.js'
  },
  module: {
    loaders: [
      {
        test: /\.jsx?$/,
        exclude: /(node_modules|bower_components)/,
        loader: 'babel', // 'babel-loader' is also a legal name to reference
        query: {
          presets: ['react', 'es2015']
        }
      }
    ]
  }
};
