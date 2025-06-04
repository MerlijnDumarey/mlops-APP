import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0', // Important for Docker
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://nginx-service:80', // NGINX service in Kubernetes
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''), // NGINX handles /api prefix
      },
    },
  },
  build: {
    outDir: 'dist', // Ensure build output directory is 'dist'
  },
});