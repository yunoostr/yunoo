// @ts-check
import { defineConfig, fontProviders } from 'astro/config';

import tailwindcss from '@tailwindcss/vite';

import react from '@astrojs/react';

// https://astro.build/config
export default defineConfig({
  site: 'https://yunoo.dev',

  fonts: [
    { provider: fontProviders.google(), name: 'Geist', cssVariable: '--font-geist' },
    { provider: fontProviders.google(), name: 'Geist Mono', cssVariable: '--font-geist-mono' },
  ],

  vite: {
    plugins: [tailwindcss()]
  },

  integrations: [react()]
});