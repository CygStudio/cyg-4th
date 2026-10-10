import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { resolve, extname, sep } from 'node:path';
const root = resolve(import.meta.dirname, '..');
const types = {'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json','.webp':'image/webp','.jpg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml','.md':'text/plain; charset=utf-8'};
createServer(async (req, res) => {
  try {
    let path = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    if (path.split('/').some(p => p.startsWith('.'))) throw new Error('Hidden path');
    if (path.startsWith('/vendor/')) path = '/node_modules/gsap/dist/' + path.slice(8);
    let target = resolve(root, '.' + path);
    if (!target.startsWith(root + sep) && target !== root) throw new Error('Outside root');
    if ((await stat(target)).isDirectory()) target = resolve(target, 'index.html');
    res.setHeader('Content-Type', types[extname(target)] || 'application/octet-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.end(await readFile(target));
  } catch { res.writeHead(404); res.end('Not found'); }
}).listen(4173, '127.0.0.1', () => console.log('Local: http://127.0.0.1:4173'));
