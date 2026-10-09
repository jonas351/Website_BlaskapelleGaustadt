(() => {
  function initialize(root = document) {
    root.querySelectorAll('[data-bg-nav]').forEach(nav => {
      if (nav.dataset.initialized) return;
      nav.dataset.initialized = 'true';
      const button = nav.querySelector('button');
      const links = nav.querySelector('.bg-nav-links');
      const close = () => { button.setAttribute('aria-expanded', 'false'); links.classList.remove('is-open'); };
      button.addEventListener('click', () => { const open = button.getAttribute('aria-expanded') !== 'true'; button.setAttribute('aria-expanded', String(open)); links.classList.toggle('is-open', open); });
      nav.addEventListener('keydown', event => { if (event.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') { close(); button.focus(); } });
      links.querySelectorAll('a').forEach(link => link.addEventListener('click', close));
      document.addEventListener('click', event => { if (!nav.contains(event.target)) close(); });
      window.matchMedia('(min-width:1025px)').addEventListener('change', close);
    });
    root.querySelectorAll('[data-bg-inquiry]').forEach(container => {
      if (container.dataset.initialized) return;
      container.dataset.initialized = 'true';
      const form = container.querySelector('form');
      const subject = form.querySelector('[name=subject]');
      const query = new URLSearchParams(location.search).get('anliegen');
      if (query === 'auftritt') subject.value = 'Auftrittsanfrage';
      if (query === 'mitmachen') subject.value = 'Mitmachen';
      const result = container.querySelector('.bg-inquiry-result');
      const prepared = container.querySelector('.bg-prepared');
      const status = container.querySelector('[role=status]');
      form.addEventListener('submit', event => {
        event.preventDefault(); if (!form.reportValidity()) return;
        const data = new FormData(form);
        prepared.value = `${data.get('subject')}\n\nHallo Blaskapelle Gaustadt,\n\n${String(data.get('message')).trim()}\n\nViele Grüße\n${String(data.get('name')).trim()}\nE-Mail: ${String(data.get('email')).trim()}`;
        const send = result.querySelector('[data-bg-send]');
        if (send && container.dataset.email) send.href = `mailto:${container.dataset.email}?subject=${encodeURIComponent(String(data.get('subject')))}&body=${encodeURIComponent(prepared.value)}`;
        status.textContent = ''; result.hidden = false; result.querySelector('h3').focus();
        result.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion:reduce)').matches ? 'instant' : 'smooth', block: 'nearest' });
      });
      result.querySelector('button').addEventListener('click', async () => {
        try { await navigator.clipboard.writeText(prepared.value); status.textContent = 'Kopiert! Du kannst die Nachricht jetzt einfügen und senden.'; }
        catch { prepared.focus(); prepared.select(); status.textContent = 'Bitte kopiere den markierten Text mit Strg+C oder über das Kopieren-Menü.'; }
      });
      form.addEventListener('input', () => { result.hidden = true; });
      form.querySelector('fieldset').disabled = false;
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => initialize()); else initialize();
  // Elementor replaces widget markup during editing; bind the replacement too.
  const editorInitialize = () => {
    if (window.elementorFrontend?.hooks) window.elementorFrontend.hooks.addAction('frontend/element_ready/global', scope => initialize(scope[0]));
  };
  if (window.jQuery) window.jQuery(window).on('elementor/frontend/init', editorInitialize);
  editorInitialize();
})();
