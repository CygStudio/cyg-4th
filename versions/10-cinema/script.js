import { mountMotion } from '../../shared/motion.js';
mountMotion({intro(tl){tl.from('.hero-copy > *',{y:25,opacity:0,stagger:.15}).from('.cinema-screen',{scale:.94,opacity:0,duration:1.2},.3).from('.cinema-controls',{y:15,opacity:0},.8)},ambient(g){return [g.to('.reel',{rotation:360,duration:24,repeat:-1,ease:'none'})]}});
const frames=[['keyvisual','咖啡香裡的，四季。'],['picnic','秋日，想和妳一起。'],['promo','把熙光，留在每一格。']];
let current=0;
const screen=document.querySelector('.screen-image');
function showFrame(delta){current=(current+delta+frames.length)%frames.length;screen.src='../../assets/web/'+frames[current][0]+'.webp';screen.alt='熙歌四週年活動插畫：'+frames[current][1];document.querySelector('.frame-title').textContent=frames[current][1];document.querySelector('.frame-label').textContent='SCENE '+String(current+1).padStart(2,'0');document.querySelector('.frame-count').textContent=String(current+1).padStart(2,'0')+' / 03';screen.style.objectFit=current===1?'contain':'cover';if(window.gsap&&!document.body.classList.contains('motion-off'))gsap.fromTo(screen,{opacity:.3,scale:1.02},{opacity:1,scale:1,duration:.55,overwrite:true});}
document.querySelector('.next-scene').addEventListener('click',()=>showFrame(1));
document.querySelector('.prev-scene').addEventListener('click',()=>showFrame(-1));
