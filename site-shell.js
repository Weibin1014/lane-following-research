document.addEventListener('DOMContentLoaded', () => {
  const progress = document.createElement('div');
  progress.className = 'page-progress';
  progress.setAttribute('aria-hidden', 'true');
  progress.innerHTML = '<i></i>';
  document.body.prepend(progress);

  const updateProgress = () => {
    const range = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    const ratio = Math.min(1, Math.max(0, window.scrollY / range));
    progress.style.setProperty('--page-progress', `${ratio * 100}%`);
    document.body.classList.toggle('has-scrolled', window.scrollY > 24);
  };
  updateProgress();
  window.addEventListener('scroll', updateProgress, { passive: true });

  // Dynamic archive content changes the page height after the browser's first
  // hash jump. Re-align deep links once late content and media have settled.
  if (window.location.hash) {
    const target = document.getElementById(decodeURIComponent(window.location.hash.slice(1)));
    if (target) {
      const alignTarget = () => target.scrollIntoView({ block: 'start' });
      const archiveList = document.getElementById('file-list');
      if (archiveList && 'MutationObserver' in window) {
        const archiveObserver = new MutationObserver(() => window.requestAnimationFrame(alignTarget));
        archiveObserver.observe(archiveList, { childList: true });
        window.setTimeout(() => archiveObserver.disconnect(), 15000);
      }
      window.addEventListener('load', () => {
        alignTarget();
        window.setTimeout(alignTarget, 500);
        window.setTimeout(alignTarget, 1500);
      }, { once: true });
    }
  }

  const readerPage = document.querySelector('.reader-shell');
  if (!readerPage) return;

  const contact = document.createElement('a');
  contact.className = 'contact-float';
  contact.href = './index.html#contact';
  contact.setAttribute('aria-label', 'Open the online research contact form');
  contact.innerHTML = '<span>Online contact</span><b>↗</b>';
  document.body.appendChild(contact);

  const contactZones = document.querySelectorAll('#contact, .research-contact, footer');
  if ('IntersectionObserver' in window && contactZones.length) {
    const visibleZones = new Set();
    const contactObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => entry.isIntersecting ? visibleZones.add(entry.target) : visibleZones.delete(entry.target));
      document.body.classList.toggle('contact-visible', visibleZones.size > 0);
    }, { threshold: 0.08 });
    contactZones.forEach(zone => contactObserver.observe(zone));
  }
});
