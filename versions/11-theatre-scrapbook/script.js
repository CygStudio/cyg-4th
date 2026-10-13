import { mountMotion } from '../../shared/motion.js';
const header = document.querySelector('.site-header');
const root = document.documentElement;
let resizeFrame;

function measureNavigation() {
  const compact = header.classList.contains('is-compact');
  header.classList.remove('is-compact');
  root.style.setProperty('--header-height', `${header.getBoundingClientRect().height}px`);
  header.classList.add('is-compact');
  root.style.setProperty('--compact-header-height', `${header.getBoundingClientRect().height}px`);
  header.classList.toggle('is-compact', compact);
}

function updateNavigation() {
  // Hysteresis avoids switching repeatedly when scrolling around the boundary.
  if (window.scrollY > 96) header.classList.add('is-compact');
  else if (window.scrollY < 24) header.classList.remove('is-compact');
}

measureNavigation();
updateNavigation();
document.fonts.ready.then(measureNavigation);
window.addEventListener('scroll', updateNavigation, { passive: true });
window.addEventListener('pageshow', updateNavigation);
window.addEventListener('resize', () => {
  cancelAnimationFrame(resizeFrame);
  resizeFrame = requestAnimationFrame(measureNavigation);
});

mountMotion({intro(tl){tl.from('.curtain.left',{xPercent:-35,duration:1.4}).from('.curtain.right',{xPercent:35,duration:1.4},0).from('.stage-character',{y:65,opacity:0,duration:1.5},.3).from('.stage-side',{y:40,opacity:0,stagger:.2},.4).from('.hero-copy > *',{y:25,opacity:0,stagger:.12},.7)},ambient(g){return [g.to('.spot-a',{rotation:18,duration:7,repeat:-1,yoyo:true,ease:'sine.inOut'}),g.to('.spot-b',{rotation:-18,duration:8,repeat:-1,yoyo:true,ease:'sine.inOut'})]}});
