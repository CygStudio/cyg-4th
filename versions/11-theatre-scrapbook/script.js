import { scrollToSection } from './section-scroll.js';
import { mountDrawer } from './drawer.js';
import { mountMotion } from '../../shared/motion.js';
const header = document.querySelector('.site-header');
const marquee = document.querySelector('.marquee');
const root = document.documentElement;
const backdrop = document.createElement('span');
backdrop.className = 'nav-backdrop';
backdrop.setAttribute('aria-hidden', 'true');
header.prepend(backdrop);
header.classList.add('has-backdrop');
const parts = [...header.querySelectorAll('.nav-backdrop, .brand-mark, .brand b, .brand em, nav > *, .menu-toggle')];
const preference = matchMedia('(prefers-reduced-motion: reduce)');
mountDrawer(header);
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
  const activeParts = parts.filter(el => header.contains(el));
  const before = motion ? activeParts.map(el => ({ rect: el.getBoundingClientRect(), opacity: +getComputedStyle(el).opacity })) : [];
  clearNavigationTween();
  header.classList.toggle('is-compact', compact);
  if (!motion) return;
  const after = activeParts.map(el => ({ rect: el.getBoundingClientRect(), opacity: +getComputedStyle(el).opacity }));
  header.classList.add('is-transitioning');
  navigationTween = window.gsap.timeline({
    defaults: { duration: .38, ease: 'power2.inOut' },
    onComplete: clearNavigationTween,
  });
  // Layout changes once; only transforms and opacity interpolate on each frame.
  activeParts.forEach((el, i) => {
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
  if (document.body.classList.contains('drawer-open')) return;
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

// One scroll controller serves drawer links, desktop navigation and hero actions.
document.addEventListener('click', event => {
  const link = event.target.closest('a[href^="#"]');
  if (!link || link.classList.contains('skip') || event.defaultPrevented || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  const hash = link.getAttribute('href');
  const target = hash.length > 1 ? document.querySelector(hash) : null;
  if (!target) return;
  event.preventDefault();
  scrollToSection(target, hash);
});

mountMotion({
  intro(tl) {
    tl.addLabel('stage', 0)
      .from('.stage-arch', { scale: .94, opacity: 0, duration: 1.2, transformOrigin: '50% 60%' }, 'stage')
      .from('.stage-word', { opacity: 0, duration: 1.3 }, 'stage+=.15')
      .from('.curtain.left', { xPercent: -65, duration: 1.5, ease: 'power3.inOut' }, 'stage')
      .from('.curtain.right', { xPercent: 65, duration: 1.5, ease: 'power3.inOut' }, 'stage')
      .from('.spot', { opacity: 0, duration: 1.2 }, 'stage+=.25')
      .addLabel('character', .3)
      .from('.stage-character img', { y: 70, scale: .96, opacity: 0, duration: 1.5, ease: 'power3.out' }, 'character')
      .from('.left-type', { x: -24, opacity: 0, duration: 1 }, 'character+=.25')
      .from('.right-type', { x: 24, opacity: 0, duration: 1 }, 'character+=.4')
      .addLabel('invitation', .75)
      .from('.hero-copy > .eyebrow', { y: 16, opacity: 0, duration: .7 }, 'invitation')
      .from('.hero h1', { y: 32, opacity: 0, duration: 1 }, 'invitation+=.12')
      .from('.hero-copy > p, .hero-date, .hero-actions', { y: 20, opacity: 0, duration: .8, stagger: .12 }, 'invitation+=.35');
  },
  ambient(g) {
    return [g.to('.spot-a', { rotation: 18, duration: 7, repeat: -1, yoyo: true, ease: 'sine.inOut' }),
      g.to('.spot-b', { rotation: -18, duration: 8, repeat: -1, yoyo: true, ease: 'sine.inOut' })];
  },
  scroll(g, ScrollTrigger) {
    // Entry moves the character image and copy children; scroll moves their containers.
    const depth = value => () => value * (innerWidth <= 760 ? .45 : 1);
    g.timeline({ defaults: { ease: 'none' }, scrollTrigger: {
      id: 'hero-depth', trigger: '.hero', start: 'top top', end: 'bottom top', scrub: .65, invalidateOnRefresh: true,
    } })
      .to('.stage-word', { y: depth(140) }, 0)
      .to('.stage-arch', { y: depth(85) }, 0)
      .to('.stage-character', { y: depth(-100) }, 0)
      .to('.stage-side', { y: depth(-150) }, 0)
      .to('.hero-copy', { y: depth(-55) }, 0)
      .to('.curtain', { y: depth(-35) }, 0);
  },
});
