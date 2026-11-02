let tween;
const preference = matchMedia('(prefers-reduced-motion: reduce)');
const allowed = () => window.gsap && !preference.matches && !document.body.classList.contains('motion-off');
export function stopSectionScroll() { tween?.kill(); tween = null; }
export function scrollToSection(target, hash) {
  stopSectionScroll();
  if (location.hash !== hash) history.pushState(null, '', hash);
  const offset = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--compact-header-height')) || 72;
  const destination = Math.max(0, Math.min(document.documentElement.scrollHeight - innerHeight, target.getBoundingClientRect().top + scrollY - offset - 18));
  target.setAttribute('tabindex', '-1');
  target.focus({ preventScroll: true });
  target.addEventListener('blur', () => target.removeAttribute('tabindex'), { once: true });
  if (!allowed()) { window.scrollTo({ top: destination, behavior: 'instant' }); return; }
  const position = { y: scrollY };
  tween = window.gsap.to(position, {
    y: destination, duration: Math.min(1.5, Math.max(.65, Math.abs(destination - scrollY) / 3000)), ease: 'power2.inOut',
    onUpdate: () => window.scrollTo({ top: position.y, behavior: 'instant' }),
    onComplete: () => { tween = null; },
  });
}
for (const name of ['wheel', 'touchstart']) window.addEventListener(name, stopSectionScroll, { passive: true });
window.addEventListener('keydown', event => { if (['ArrowUp', 'ArrowDown', 'PageUp', 'PageDown', 'Home', 'End', ' '].includes(event.key)) stopSectionScroll(); });
window.addEventListener('pagehide', stopSectionScroll);
preference.addEventListener('change', stopSectionScroll);
new MutationObserver(() => { if (!allowed()) stopSectionScroll(); }).observe(document.body, { attributes: true, attributeFilter: ['class'] });
