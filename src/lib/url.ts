// Prefix internal paths with the configured base (`/ZiyOne` on GitHub Pages).
// Use for every internal link/asset so dev and production both resolve.
// Leaves absolute URLs (http/https/mailto) untouched.
const BASE = import.meta.env.BASE_URL; // e.g. "/ZiyOne/"

export function withBase(path: string): string {
  if (/^(https?:|mailto:|#)/.test(path)) return path;
  const clean = path.replace(/^\//, '');
  return `${BASE.replace(/\/$/, '')}/${clean}`.replace(/\/$/, '') || '/';
}
