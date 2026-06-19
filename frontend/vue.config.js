const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      '/auth':        { target: 'http://localhost:8000', changeOrigin: true },
      '/users':       { target: 'http://localhost:8000', changeOrigin: true },
      '/works':       { target: 'http://localhost:8000', changeOrigin: true },
      '/groups':      { target: 'http://localhost:8000', changeOrigin: true },
      '/departments': { target: 'http://localhost:8000', changeOrigin: true },
    }
  }
})
