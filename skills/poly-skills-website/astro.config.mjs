import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import react from '@astrojs/react';
import typography from '@tailwindcss/typography';

export default defineConfig({
  site: 'https://vinzeny.github.io',
  base: '/crypto-skills',
  vite: {
    plugins: [tailwindcss({
      plugins: [typography]
    })]
  },
  integrations: [react()]
});
