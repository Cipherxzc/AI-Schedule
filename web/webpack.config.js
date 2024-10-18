const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const { VueLoaderPlugin } = require('vue-loader');
const { DefinePlugin } = require('webpack');

module.exports = {
  mode: 'development', // 设置模式
  entry: './src/main.js',
  output: {//在这个配置中，所有打包后的文件将被输出到 dist 目录，并且输出的文件名被设置为 bundle.js。
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js',
  },//output: 定义了输出选项，包括输出目录和打包后的文件名
  resolve: {
    extensions: ['.js', '.vue'],
  },
  module: {//定义了如何处理不同类型的模块，即加载器（loaders）的规则。
    rules: [
      {
        test: /\.vue$/,
        loader: 'vue-loader',
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
        },
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html',
    }),
    new VueLoaderPlugin(),
    new DefinePlugin({
      BASE_URL: JSON.stringify('/'), // 修改 BASE_URL，根据需要调整
    }),
  ],
};
/** plugins: 定义了要使用的 Webpack 插件。这里使用了三个插件：

HtmlWebpackPlugin：这个插件会自动创建一个 HTML 文件，并将打包后的 JavaScript 文件（如 bundle.js）注入到这个 HTML 文件中。
VueLoaderPlugin：这个插件是 Vue.js 项目必需的，它确保 .vue 文件能被正确处理。
DefinePlugin：这个插件用于在编译时创建全局常量。在这个配置中，它定义了一个 BASE_URL 常量，其值被设置为根路径 /。这通常用于配置 API 请求的基础 URL。
这个配置文件告诉 Webpack 如何处理项目中的不同文件类型，
如何打包它们，以及如何生成最终的输出文件。
*/