const finishFlips = [];
document.querySelectorAll('.proposal-b .flip').forEach(button => {
  const img = button.closest('.piece').querySelector('img');
  let requestedBack = false;
  let request = 0;
  let timeline;
  const clear = () => { window.gsap?.set(img, {clearProps:'transform,willChange'}); timeline = undefined; };
  const show = back => {
    img.src = back ? button.dataset.back : button.dataset.front;
    img.alt = `熙歌四週年 ${button.dataset.name}${back ? '背面' : '正面'}實拍`;
    button.dataset.backVisible = String(back);
    button.setAttribute('aria-label', `${back ? '看正面' : '看背面'}：${button.dataset.name}`);
    button.querySelector('span').textContent = back ? '看正面' : '看背面';
  };
  finishFlips.push(() => { if (timeline) timeline.progress(1); else clear(); });
  const loaded = new Map();
  function prepare(src) {
    if (!loaded.has(src)) {
      const photo = new Image();
      photo.src = src;
      loaded.set(src, photo.decode().catch(error => {
        loaded.delete(src);
        throw error;
      }));
    }
    return loaded.get(src);
  }
  const observer = new IntersectionObserver(entries => {
    if (!entries.some(entry => entry.isIntersecting)) return;
    void prepare(button.dataset.back).catch(() => {});
    observer.disconnect();
  }, {rootMargin:'400px'});
  observer.observe(img);
  button.addEventListener('click', async () => {
    requestedBack = !requestedBack;
    const back = requestedBack;
    const current = ++request;
    timeline?.kill();
    timeline = undefined;
    const src = back ? button.dataset.back : button.dataset.front;
    try { await prepare(src); } catch {
      if (current === request) { requestedBack = button.dataset.backVisible === 'true'; clear(); }
      return;
    }
    if (current !== request) return;
    if (!window.gsap || document.body.classList.contains('motion-off')) { show(back); clear(); return; }
    img.style.willChange = 'transform';
    // Retarget the current angle immediately; repeated clicks never accumulate a queue.
    if ((button.dataset.backVisible === 'true') === back) {
      timeline = window.gsap.to(img, {rotationY:0, duration:.14, ease:'power2.out', onComplete:clear});
      return;
    }
    const direction = Number(window.gsap.getProperty(img, 'rotationY')) < 0 ? -1 : 1;
    timeline = window.gsap.timeline({onComplete:clear});
    timeline.to(img, {rotationY:90*direction, duration:.12, ease:'power2.in'})
      .call(() => show(back))
      .set(img, {rotationY:-90*direction})
      .to(img, {rotationY:0, duration:.16, ease:'power2.out'});
  });
});

new MutationObserver(() => {
  if (document.body.classList.contains('motion-off')) finishFlips.forEach(finish => finish());
}).observe(document.body, {attributes:true, attributeFilter:['class']});
