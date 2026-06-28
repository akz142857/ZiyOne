// @ts-check
import { defineConfig } from 'astro/config';

// Two deploy targets share this config, switched via env at build time:
//   - GitHub Pages (default): base '/ZiyOne' under akz142857.github.io
//   - k8s at ziy.one apex:     ASTRO_BASE=/ ASTRO_SITE=https://ziy.one
// `base` MUST stay in sync with the repo name on GitHub Pages or assets 404.
// All internal links go through withBase() (src/lib/url.ts), so flipping the
// base here is sufficient — no per-link edits needed.
// Read env without pulling in @types/node (keeps `astro check` clean).
const env = /** @type {any} */ (globalThis).process?.env ?? {};

export default defineConfig({
  site: env.ASTRO_SITE ?? 'https://akz142857.github.io',
  base: env.ASTRO_BASE ?? '/ZiyOne',
  trailingSlash: 'ignore',
});
