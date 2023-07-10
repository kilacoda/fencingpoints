module.exports = {
    entry: "./src/scripts/index.js",
    module: {
      rules: [
        {
          test: /\.tsx?$/,
          use: "ts-loader",
          exclude: /node_modules/,
        },
      ],
    },
    resolve: {
      extensions: [".tsx", ".ts", ".js"],
    },
    output: {
      filename: "bundle.js",
    },
    devServer: {
      publicPath: "/dist",
    },
  };
