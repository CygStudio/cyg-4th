import { cp, mkdir, rm } from 'node:fs/promises';
await rm('dist', { recursive: true, force: true });
await mkdir('dist/assets', { recursive: true });
for (const path of ['index.html', 'designs', 'shared', 'versions']) await cp(path, 'dist/' + path, { recursive: true });
await cp('assets/web', 'dist/assets/web', { recursive: true });
await mkdir('dist/vendor', { recursive: true });
for (const file of ['gsap.min.js', 'ScrollTrigger.min.js']) await cp('node_modules/gsap/dist/' + file, 'dist/vendor/' + file);
await cp('licenses/GSAP-NOTICE.txt', 'dist/vendor/GSAP-NOTICE.txt');

await cp('cafe', 'dist/cafe', { recursive: true });
await mkdir('dist/vendor/three', { recursive: true });
for (const directory of ['build', 'examples/jsm']) await cp('node_modules/three/' + directory, 'dist/vendor/three/' + directory, { recursive: true });
await cp('node_modules/three/LICENSE', 'dist/vendor/three/LICENSE');
console.log('Built local static site in dist/');
