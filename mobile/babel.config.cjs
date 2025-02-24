module.exports = function(api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      '@babel/plugin-transform-class-static-block',
      'expo-router/babel',
      [
        'module-resolver',
        {
          alias: {
            '@': '.',
            '@components': './components',
            '@hooks': './hooks'
          },
          extensions: ['.js', '.jsx', '.ts', '.tsx']
        }
      ]
    ]
  };
};