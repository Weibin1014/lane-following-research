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

  // Keep the full navigation usable on narrow screens instead of silently
  // removing it. The panel is generated from the page's existing links so its
  // labels and destinations always stay in sync with the desktop navigation.
  const siteHeader = document.querySelector('.site-header');
  const desktopNav = siteHeader?.querySelector(':scope > nav');
  if (siteHeader && desktopNav) {
    const menuButton = document.createElement('button');
    menuButton.className = 'mobile-nav-toggle';
    menuButton.type = 'button';
    menuButton.setAttribute('aria-expanded', 'false');
    menuButton.setAttribute('aria-controls', 'mobile-site-navigation');
    menuButton.innerHTML = '<span>Menu</span><i aria-hidden="true"></i>';

    const mobileNav = document.createElement('nav');
    mobileNav.id = 'mobile-site-navigation';
    mobileNav.className = 'mobile-nav-panel';
    mobileNav.setAttribute('aria-label', 'Mobile navigation');
    mobileNav.innerHTML = desktopNav.innerHTML;
    mobileNav.hidden = true;
    mobileNav.setAttribute('aria-hidden', 'true');
    siteHeader.append(menuButton, mobileNav);

    const setMenu = open => {
      menuButton.setAttribute('aria-expanded', String(open));
      mobileNav.hidden = !open;
      mobileNav.setAttribute('aria-hidden', String(!open));
      mobileNav.classList.toggle('is-open', open);
      document.body.classList.toggle('mobile-nav-open', open);
    };
    menuButton.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true'));
    mobileNav.addEventListener('click', event => {
      if (event.target.closest('a')) setMenu(false);
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape') setMenu(false);
    });
    window.addEventListener('resize', () => {
      if (window.innerWidth > 900) setMenu(false);
    });
  }

  const sectionLinks = [...document.querySelectorAll('.site-header a[href^="#"], .mobile-nav-panel a[href^="#"]')]
    .filter(link => link.getAttribute('href').length > 1);
  const observedSections = [...new Set(sectionLinks.map(link => document.querySelector(link.getAttribute('href'))).filter(Boolean))];
  if ('IntersectionObserver' in window && observedSections.length) {
    const activeSections = new Map();
    const updateActiveLink = () => {
      const visible = [...activeSections.entries()].filter(([, active]) => active).map(([section]) => section);
      if (!visible.length) return;
      visible.sort((a, b) => Math.abs(a.getBoundingClientRect().top - 120) - Math.abs(b.getBoundingClientRect().top - 120));
      const currentHash = `#${visible[0].id}`;
      sectionLinks.forEach(link => {
        if (link.getAttribute('href') === currentHash) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    };
    const sectionObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => activeSections.set(entry.target, entry.isIntersecting));
      updateActiveLink();
    }, { rootMargin: '-15% 0px -70% 0px', threshold: 0 });
    observedSections.forEach(section => sectionObserver.observe(section));
  }

  // Return to the exact previous archive/filter position when possible. Direct
  // links and new tabs retain a dependable parent-page fallback.
  document.querySelectorAll('[data-back]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      let referrer;
      try { referrer = document.referrer ? new URL(document.referrer) : null; } catch { referrer = null; }
      const sameSiteHistory = referrer && referrer.origin === window.location.origin && referrer.href !== window.location.href && window.history.length > 1;
      if (sameSiteHistory) {
        event.preventDefault();
        window.history.back();
      }
    });
  });

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
