const controllers = [];
const motionOff = () => document.body.classList.contains('motion-off');

document.querySelectorAll('.proposal-b .flip').forEach(button => {
  const piece = button.closest('.piece');
  const img = piece.querySelector('img');
  const tape = piece.matches('.piece-postcard,.piece-ticket') ? document.createElement('span') : null;
  if (tape) {
    tape.className = 'merch-tape';
    tape.setAttribute('aria-hidden', 'true');
    piece.prepend(tape);
  }
  let pending = 0;
  let busy = false;
  let timeline;
  const applySide = back => {
    img.src = back ? button.dataset.back : button.dataset.front;
    img.alt = `熙歌四週年 ${button.dataset.name}${back ? '背面' : '正面'}實拍`;
    button.dataset.backVisible = String(back);
    button.setAttribute('aria-label', `${back ? '看正面' : '看背面'}：${button.dataset.name}`);
    button.querySelector('span').textContent = back ? '看正面' : '看背面';
  };
  const finish = () => {
    window.gsap?.set(img, {clearProps:'transform,willChange'});
    if (tape) window.gsap?.set(tape, {clearProps:'opacity'});
    busy = false;
    timeline = undefined;
    button.removeAttribute('aria-busy');
    if (pending) void turn();
  };
  async function turn() {
    if (busy || !pending) return;
    pending--;
    busy = true;
    button.setAttribute('aria-busy', 'true');
    const back = button.dataset.backVisible !== 'true';
    const next = new Image();
    next.src = back ? button.dataset.back : button.dataset.front;
    let timeout;
    try {
      await Promise.race([next.decode(), new Promise((_, reject) => {
        timeout = setTimeout(() => reject(new Error('Image timeout')), 8000);
      })]);
    } catch {
      pending = 0;
      finish();
      return;
    } finally { clearTimeout(timeout); }
    if (!window.gsap || motionOff()) {
      applySide(back);
      finish();
      return;
    }
    img.style.willChange = 'transform';
    timeline = window.gsap.timeline({onComplete:finish});
    if (tape) timeline.to(tape, {opacity:0, duration:.14, ease:'power1.out'});
    timeline.to(img, {rotationY:90, duration:.22, ease:'power2.in'})
      .call(() => applySide(back))
      .set(img, {rotationY:-90})
      .to(img, {rotationY:0, duration:.32, ease:'power2.out'});
    if (tape) timeline.to(tape, {opacity:1, duration:.18, ease:'power1.inOut'});
  }
  button.addEventListener('click', () => { pending++; void turn(); });
  controllers.push(() => timeline?.progress(1));
});
new MutationObserver(() => {
  if (motionOff()) controllers.forEach(finish => finish());
}).observe(document.body, {attributes:true, attributeFilter:['class']});
