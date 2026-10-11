(() => {
  document.documentElement.classList.add('tb-js');
  function initialize(root = document) {
    root.querySelectorAll('[data-tb-hero-media]').forEach(container => {
      if (container.dataset.initialized) return;
      container.dataset.initialized = 'true';
      const video = container.querySelector('video');
      const button = container.querySelector('button');
      if (!video || !button) return;
      const reduced = window.matchMedia('(prefers-reduced-motion:reduce)');
      const showState = playing => {
        button.textContent = playing ? 'Video pausieren' : 'Video abspielen';
        button.setAttribute('aria-label', `Bamberg-${playing ? 'Video pausieren' : 'Video abspielen'}`);
        button.setAttribute('aria-pressed', String(playing));
      };
      const play = async () => {
        if (!video.src) video.src = video.dataset.src;
        try { await video.play(); container.classList.add('is-playing'); showState(true); }
        catch { video.pause(); container.classList.remove('is-playing'); showState(false); }
      };
      button.hidden = false;
      button.addEventListener('click', () => { if (video.paused) play(); else { video.pause(); showState(false); } });
      reduced.addEventListener('change', () => { if (reduced.matches) { video.pause(); showState(false); } });
      document.addEventListener('visibilitychange', () => { if (document.hidden) { video.pause(); showState(false); } });
      if (container.dataset.autoplay === 'yes' && !reduced.matches && !navigator.connection?.saveData) play();
    });
    root.querySelectorAll('[data-tb-nav]').forEach(nav => {
      if (nav.dataset.initialized) return;
      nav.dataset.initialized = 'true';
      const button = nav.querySelector('button');
      const links = nav.querySelector('.tb-nav-links');
      const groups = [...nav.querySelectorAll('details')];
      const close = () => { button.setAttribute('aria-expanded', 'false'); links.classList.remove('is-open'); groups.forEach(group => { group.open = false; }); };
      button.addEventListener('click', () => { const open = button.getAttribute('aria-expanded') !== 'true'; button.setAttribute('aria-expanded', String(open)); links.classList.toggle('is-open', open); });
      groups.forEach(group => group.addEventListener('toggle', () => { if (group.open) groups.filter(other => other !== group).forEach(other => { other.open = false; }); }));
      nav.addEventListener('keydown', event => {
        if (event.key !== 'Escape') return;
        const group = event.target.closest('details[open]');
        if (group) { group.open = false; group.querySelector('summary').focus(); event.preventDefault(); }
        else if (button.getAttribute('aria-expanded') === 'true') { close(); button.focus(); }
      });
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
      const area = form.querySelector('[name=area]');
      if (area && [...area.options].some(option => option.value === query)) area.value = query;
      const result = container.querySelector('.tb-inquiry-result');
      const prepared = container.querySelector('.tb-prepared');
      const status = container.querySelector('[role=status]');
      form.addEventListener('submit', event => {
        event.preventDefault(); if (!form.reportValidity()) return;
        const data = new FormData(form);
        const context = area?.selectedOptions[0]?.textContent || 'Bamberg-Stadt';
        prepared.value = `${data.get('subject')}\nBereich: ${context}\n\nHallo CSU Bamberg,\n\n${String(data.get('message')).trim()}\n\nViele Grüße\n${String(data.get('name')).trim()}\nE-Mail: ${String(data.get('email')).trim()}`;
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
