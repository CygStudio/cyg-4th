document.querySelectorAll('.proposal-b .flip').forEach(button => {
  const img = button.closest('.piece').querySelector('img');
  let requestedBack = false;
  let request = 0;
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
    const src = back ? button.dataset.back : button.dataset.front;
    try { await prepare(src); } catch {
      if (current === request) requestedBack = button.dataset.backVisible === 'true';
      return;
    }
    if (current !== request) return;
    img.src = src;
    img.alt = `熙歌四週年 ${button.dataset.name}${back ? '背面' : '正面'}實拍`;
    button.dataset.backVisible = String(back);
    button.setAttribute('aria-label', `${back ? '看正面' : '看背面'}：${button.dataset.name}`);
    button.querySelector('span').textContent = back ? '看正面' : '看背面';
  });
});
