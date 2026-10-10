import { cp, mkdir, rm } from 'node:fs/promises';
await rm('dist', { recursive: true, force: true });
await mkdir('dist/assets', { recursive: true });
for (const path of ['index.html', 'shared', 'versions']) await cp(path, 'dist/' + path, { recursive: true });
await cp('assets/web', 'dist/assets/web', { recursive: true });
await mkdir('dist/vendor', { recursive: true });
for (const file of ['gsap.min.js', 'ScrollTrigger.min.js']) await cp('node_modules/gsap/dist/' + file, 'dist/vendor/' + file);
await cp('licenses/GSAP-NOTICE.txt', 'dist/vendor/GSAP-NOTICE.txt');
console.log('Built local static site in dist/');
