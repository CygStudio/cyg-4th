import { readdir, readFile, stat } from 'node:fs/promises';
import { resolve } from 'node:path';
const required = ['熙歌四週年應援咖啡廳','#四季熙光皆成歌','11/23','11/29','13:00','18:00','Little Donkey Cafe 小驢館','信義路四段265巷12弄21號','信義安和站','200','80','https://x.com/cyg_studio_fan','https://x.com/cygnusxdfp','https://youtube.com/@cygnusxdfp'];
const dirs = (await readdir('versions',{withFileTypes:true})).filter(x=>x.isDirectory());
for (const {name} of dirs) {
  const path = 'versions/' + name;
  const html = await readFile(path+'/index.html','utf8');
  for(const term of required) if(!html.includes(term)) throw new Error(name+' missing '+term);
  for(const f of ['DESIGN.md','style.css','script.js','version.json']) await stat(path+'/'+f);
  for (const [,url] of html.matchAll(/(?:src|href)="([^"]+)"/g)) {
    if(url.startsWith('http') || url.startsWith('#')) continue;
    if(url.includes('/vendor/')) continue;
    await stat(resolve(path,url.split(/[?#]/)[0]));
  }
  console.log('PASS '+name+': event facts, local references, design files');
}
const assets = JSON.parse(await readFile('assets/manifest.json'));
if(assets.length!==20 || assets.some(x=>!x.downloaded)) throw new Error('Incomplete downloads');
console.log('PASS original asset inventory: 20/20');
