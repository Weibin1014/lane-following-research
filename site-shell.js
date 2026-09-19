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

  const mail = document.createElement('a');
  mail.className = 'contact-float';
  mail.href = 'mailto:mark608041@gmail.com?subject=Lane%20Following%20Research%20Enquiry';
  mail.setAttribute('aria-label', 'Email Zhang Weibin about the lane-following research');
  mail.innerHTML = '<span>Research contact</span><b>↗</b>';
  document.body.appendChild(mail);

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
