// @ts-check
import { defineConfig } from 'astro/config';

// Deployed to GitHub Pages at https://akz142857.github.io/ZiyOne/
// `base` MUST stay in sync with the repo name or production assets 404.
export default defineConfig({
  site: 'https://akz142857.github.io',
  base: '/ZiyOne',
  trailingSlash: 'ignore',
});
