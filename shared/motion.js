export function mountMotion(config = {}) {
  const { gsap, ScrollTrigger } = window;
  const toggle = document.querySelector('.motion-toggle');
  const preference = matchMedia('(prefers-reduced-motion: reduce)');
  let manualOff = sessionStorage.getItem('cyg-motion-off') === 'true';
  let cleanup = () => {};
  function setup() {
    cleanup();
    window.__introDone = false;
    const off = preference.matches || manualOff;
    document.body.classList.toggle('motion-off', off);
    toggle.textContent = off ? '動態：關閉' : '動態：開啟';
    toggle.setAttribute('aria-pressed', String(!off));
    if (off || !gsap || !ScrollTrigger) { window.__motionReady = true; window.__introDone = true; return; }
    gsap.registerPlugin(ScrollTrigger);
    const loops = [];
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { duration: .9, ease: 'power3.out' }, onComplete: () => { window.__introDone = true; } });
      if (config.intro) config.intro(tl, gsap);
      else tl.from('.hero-copy > *', { y: 24, opacity: 0, stagger: .1 });
      document.querySelectorAll('[data-reveal]').forEach(el => {
        gsap.from(el, { y: 30, opacity: 0, duration: .7, ease: 'power2.out', scrollTrigger: {trigger: el, start: 'top 92%', once: true} });
      });
      if (innerWidth > 760) document.querySelectorAll('[data-parallax]').forEach(el => {
        gsap.to(el, { y: Number(el.dataset.parallax), ease:'none', scrollTrigger:{trigger:el.closest('.hero') || el.parentElement,start:'top top',end:'bottom top',scrub:.7} });
      });
      document.querySelectorAll('.petal').forEach((el, i) => {
        loops.push(gsap.to(el, { y: () => el.parentElement.clientHeight + 60, x: i % 2 ? 50 : -40, rotation: 160 + i * 31, duration: 9 + i % 5, delay: i * -1.7, ease:'none', repeat:-1 }));
      });
      document.querySelectorAll('.marquee-track').forEach(el => loops.push(gsap.to(el, {xPercent:-50,duration:32,repeat:-1,ease:'none'})));
      if (config.ambient) loops.push(...config.ambient(gsap));
      if (config.scroll) config.scroll(gsap, ScrollTrigger);
    });
    const hero = document.querySelector('.hero');
    const observer = new IntersectionObserver(([entry]) => loops.forEach(t => entry.isIntersecting && !document.hidden ? t.play() : t.pause()), { threshold:0 });
    if(hero) observer.observe(hero);
    const visibility = () => document.hidden ? loops.forEach(t => t.pause()) : observer.disconnect() || observer.observe(hero);
    document.addEventListener('visibilitychange', visibility);
    const refresh = () => ScrollTrigger.refresh();
    document.fonts.ready.then(refresh);
    document.querySelectorAll('img').forEach(img => { if(!img.complete) img.addEventListener('load',refresh,{once:true}); });
    cleanup = () => { observer.disconnect();document.removeEventListener('visibilitychange',visibility);ctx.revert(); };
    window.__motionReady = true;
  }
  toggle.addEventListener('click',()=>{manualOff = !(preference.matches || manualOff);sessionStorage.setItem('cyg-motion-off',String(manualOff));setup();});
  preference.addEventListener('change',setup);
  window.addEventListener('pagehide',()=>cleanup(),{once:true});
  document.querySelectorAll('details').forEach(el => el.addEventListener('toggle',()=>ScrollTrigger?.refresh()));
  document.querySelector('.copy-tag')?.addEventListener('click', async () => {
    const status = document.querySelector('.status-message');
    try { await navigator.clipboard.writeText('#四季熙光皆成歌');status.textContent = '已複製 #四季熙光皆成歌'; }
    catch { status.textContent = '請選取並複製：#四季熙光皆成歌'; }
  });
  setup();
}
