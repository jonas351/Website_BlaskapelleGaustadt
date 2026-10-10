(() => {
  function initialize(root = document) {
    root.querySelectorAll('[data-tb-nav]').forEach(nav => {
      if (nav.dataset.initialized) return;
      nav.dataset.initialized = 'true';
      const button = nav.querySelector('button');
      const links = nav.querySelector('.tb-nav-links');
      const close = () => { button.setAttribute('aria-expanded', 'false'); links.classList.remove('is-open'); };
      button.addEventListener('click', () => { const open = button.getAttribute('aria-expanded') !== 'true'; button.setAttribute('aria-expanded', String(open)); links.classList.toggle('is-open', open); });
      nav.addEventListener('keydown', event => { if (event.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') { close(); button.focus(); } });
      links.querySelectorAll('a').forEach(link => link.addEventListener('click', close));
      document.addEventListener('click', event => { if (!nav.contains(event.target)) close(); });
      window.matchMedia('(min-width:1025px)').addEventListener('change', close);
    });
    root.querySelectorAll('[data-tb-inquiry]').forEach(container => {
      if (container.dataset.initialized) return;
      container.dataset.initialized = 'true';
      const form = container.querySelector('form');
      const subject = form.querySelector('[name=subject]');
      const query = new URLSearchParams(location.search).get('anliegen');
      if (query === 'stadtpolitik') subject.value = 'Stadtpolitik';
      if (query === 'mitmachen') subject.value = 'Mitmachen';
      const result = container.querySelector('.tb-inquiry-result');
      const prepared = container.querySelector('.tb-prepared');
      const status = container.querySelector('[role=status]');
      form.addEventListener('submit', event => {
        event.preventDefault(); if (!form.reportValidity()) return;
        const data = new FormData(form);
        prepared.value = `${data.get('subject')}\n\nHallo CSU Bamberg,\n\n${String(data.get('message')).trim()}\n\nViele Grüße\n${String(data.get('name')).trim()}\nE-Mail: ${String(data.get('email')).trim()}`;
        const send = result.querySelector('[data-tb-send]');
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
    root.querySelectorAll('[data-tb-archive]').forEach(filter => {
      if (filter.dataset.initialized) return;
      filter.dataset.initialized = 'true';
      const cards = [...document.querySelectorAll('.tb-document')];
      const query = filter.querySelector('input');
      const year = filter.querySelector('select');
      const status = filter.querySelector('[role=status]');
      const years = [...new Set(cards.flatMap(card => [...card.classList].filter(name => /^tb-year-\d{4}$/.test(name)).map(name => name.slice(8))))].sort().reverse();
      years.forEach(value => { const option = document.createElement('option'); option.value = value; option.textContent = value; year.append(option); });
      const apply = () => {
        const text = query.value.trim().toLocaleLowerCase('de');
        let visible = 0;
        cards.forEach(card => {
          const match = (!year.value || card.classList.contains(`tb-year-${year.value}`)) && card.textContent.toLocaleLowerCase('de').includes(text);
          card.hidden = !match;
          if (match) visible++;
        });
        status.textContent = `${visible} ${visible === 1 ? 'Eintrag' : 'Einträge'} gefunden.`;
      };
      query.addEventListener('input', apply); year.addEventListener('change', apply); apply();
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
