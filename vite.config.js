import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  server: {
    allowedHosts: true,
  },
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        notfound: resolve(__dirname, '404.html'),
        privacy: resolve(__dirname, 'privacy.html'),
      },
    },
  },
});
