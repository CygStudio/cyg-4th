import { scrollToSection, stopSectionScroll } from './section-scroll.js';
export function mountDrawer(header) {
  const toggle = header.querySelector('.menu-toggle');
  const navigation = header.querySelector('nav');
  const dialog = document.querySelector('#mobile-menu');
  const panel = dialog.querySelector('.drawer-panel');
  const content = dialog.querySelector('.drawer-content');
  const closeButton = dialog.querySelector('.menu-close');
  const mobile = matchMedia('(max-width: 760px)');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  let tween;
  let scrollY = 0;
  let closing = false;
  let afterClose;
  const animated = () => window.gsap && !reducedMotion.matches && !document.body.classList.contains('motion-off');

  function finishClose(restoreFocus = true) {
    tween?.kill();
    if (!dialog.open) return;
    dialog.close();
    toggle.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('drawer-open');
    document.body.style.removeProperty('--drawer-scroll');
    window.scrollTo({ top: scrollY, behavior: 'instant' });
    panel.style.removeProperty('transform');
    closing = false;
    if (restoreFocus && mobile.matches) toggle.focus({ preventScroll: true });
    const complete = afterClose;
    afterClose = null;
    complete?.();
  }
  function close({ immediate = false, restoreFocus = true, complete } = {}) {
    if (!dialog.open || closing && !immediate) return;
    tween?.kill();
    closing = true;
    afterClose = complete;
    if (immediate || !animated()) finishClose(restoreFocus);
    else tween = window.gsap.to(panel, { xPercent: 100, duration: .3, ease: 'power2.in', onComplete: () => finishClose(restoreFocus) });
  }
  function open() {
    if (!mobile.matches || dialog.open) return;
    stopSectionScroll();
    scrollY = window.scrollY;
    document.body.style.setProperty('--drawer-scroll', `-${scrollY}px`);
    document.body.classList.add('drawer-open');
    dialog.showModal();
    toggle.setAttribute('aria-expanded', 'true');
    closeButton.focus({ preventScroll: true });
    if (animated()) tween = window.gsap.fromTo(panel, { xPercent: 100 }, { xPercent: 0, duration: .48, ease: 'power3.out' });
  }
  function adapt() {
    close({ immediate: true, restoreFocus: false });
    (mobile.matches ? content : header).append(navigation);
  }
  toggle.addEventListener('click', open);
  closeButton.addEventListener('click', () => close());
  dialog.addEventListener('keydown', event => {
    if (event.key !== 'Tab') return;
    const controls = [...dialog.querySelectorAll('a[href], button:not([disabled])')].filter(el => el.checkVisibility());
    const first = controls[0], last = controls.at(-1);
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });
  dialog.addEventListener('cancel', event => { event.preventDefault(); close(); });
  dialog.addEventListener('click', event => { if (event.target === dialog) close(); });
  navigation.addEventListener('click', event => {
    const link = event.target.closest('a');
    if (!link || !dialog.open) return;
    if (closing) { event.preventDefault(); event.stopPropagation(); return; }
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const href = link.getAttribute('href');
    if (href.startsWith('#')) {
      const target = document.querySelector(href);
      if (!target) return;
      event.preventDefault();
      event.stopPropagation();
      close({ restoreFocus: false, complete: () => scrollToSection(target, href) });
    } else {
      close({ immediate: true, restoreFocus: false });
    }
  });
  mobile.addEventListener('change', adapt);
  window.addEventListener('resize', () => {
    if (navigation.parentElement !== (mobile.matches ? content : header)) adapt();
  });
  reducedMotion.addEventListener('change', () => { if (dialog.open && closing) finishClose(); });
  window.addEventListener('pagehide', () => close({ immediate: true, restoreFocus: false }));
  adapt();
  header.classList.add('drawer-ready');
}
