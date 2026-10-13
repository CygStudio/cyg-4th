import { mountMotion } from '../../shared/motion.js';
const header = document.querySelector('.site-header');
const marquee = document.querySelector('.marquee');
const root = document.documentElement;
const backdrop = document.createElement('span');
backdrop.className = 'nav-backdrop';
backdrop.setAttribute('aria-hidden', 'true');
header.prepend(backdrop);
header.classList.add('has-backdrop');
const parts = [...header.querySelectorAll('.nav-backdrop, .brand-mark, .brand b, .brand em, nav > *')];
const preference = matchMedia('(prefers-reduced-motion: reduce)');
let resizeFrame;
let navigationTween;
let measuredWidth;

function clearNavigationTween() {
  navigationTween?.kill();
  navigationTween = null;
  window.gsap?.set(parts, { clearProps: 'transform,opacity' });
  header.classList.remove('is-transitioning');
}

function measureNavigation() {
  clearNavigationTween();
  measuredWidth = window.innerWidth;
  const compact = header.classList.contains('is-compact');
  header.classList.remove('is-compact');
  const expandedHeight = header.getBoundingClientRect().height;
  header.classList.add('is-compact');
  const compactHeight = header.getBoundingClientRect().height;
  header.classList.toggle('is-compact', compact);
  root.style.setProperty('--header-height', `${expandedHeight}px`);
  root.style.setProperty('--compact-header-height', `${compactHeight}px`);
  root.style.setProperty('--marquee-height', `${marquee.getBoundingClientRect().height}px`);
}

function setCompact(compact, animate) {
  if (header.classList.contains('is-compact') === compact) return;
  const motion = animate && window.gsap && !preference.matches && !document.body.classList.contains('motion-off');
  // Capture the currently rendered positions, including an interrupted transition.
  const before = motion ? parts.map(el => ({ rect: el.getBoundingClientRect(), opacity: +getComputedStyle(el).opacity })) : [];
  clearNavigationTween();
  header.classList.toggle('is-compact', compact);
  if (!motion) return;
  const after = parts.map(el => ({ rect: el.getBoundingClientRect(), opacity: +getComputedStyle(el).opacity }));
  header.classList.add('is-transitioning');
  navigationTween = window.gsap.timeline({
    defaults: { duration: .38, ease: 'power2.inOut' },
    onComplete: clearNavigationTween,
  });
  // Layout changes once; only transforms and opacity interpolate on each frame.
  parts.forEach((el, i) => {
    const first = before[i], last = after[i];
    if (!first.rect.width || !last.rect.width) return;
    navigationTween.fromTo(el, {
      x: first.rect.left - last.rect.left,
      y: first.rect.top - last.rect.top,
      scaleX: first.rect.width / last.rect.width,
      scaleY: first.rect.height / last.rect.height,
      opacity: first.opacity,
    }, { x: 0, y: 0, scaleX: 1, scaleY: 1, opacity: last.opacity }, 0);
  });
}

function updateNavigation(animate = true) {
  // Hysteresis avoids switching repeatedly when scrolling around the boundary.
  if (window.scrollY > 96) setCompact(true, animate);
  else if (window.scrollY < 24) setCompact(false, animate);
}

measureNavigation();
updateNavigation(false);
document.fonts.ready.then(measureNavigation);
window.addEventListener('scroll', () => updateNavigation(), { passive: true });
window.addEventListener('pageshow', () => updateNavigation(false));
window.addEventListener('resize', () => {
  // Mobile browser chrome changes viewport height during a scroll, not nav geometry.
  if (window.innerWidth === measuredWidth) return;
  cancelAnimationFrame(resizeFrame);
  resizeFrame = requestAnimationFrame(measureNavigation);
});
new ResizeObserver(() => {
  root.style.setProperty('--marquee-height', `${marquee.getBoundingClientRect().height}px`);
}).observe(marquee);
new MutationObserver(() => {
  if (document.body.classList.contains('motion-off')) clearNavigationTween();
}).observe(document.body, { attributes: true, attributeFilter: ['class'] });
window.addEventListener('pagehide', clearNavigationTween);

mountMotion({intro(tl){tl.from('.curtain.left',{xPercent:-35,duration:1.4}).from('.curtain.right',{xPercent:35,duration:1.4},0).from('.stage-character',{y:65,opacity:0,duration:1.5},.3).from('.stage-side',{y:40,opacity:0,stagger:.2},.4).from('.hero-copy > *',{y:25,opacity:0,stagger:.12},.7)},ambient(g){return [g.to('.spot-a',{rotation:18,duration:7,repeat:-1,yoyo:true,ease:'sine.inOut'}),g.to('.spot-b',{rotation:-18,duration:8,repeat:-1,yoyo:true,ease:'sine.inOut'})]}});
